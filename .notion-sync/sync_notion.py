#!/usr/bin/env python3
"""Mirror repository Agent Skills into a native Notion Skills database.

GitHub is authoritative. Notion-side edits are overwritten on the next run.
Only pages carrying this script's Sync ID prefix are updated or trashed.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import re
import sys
import time
import zipfile
from pathlib import Path
from typing import Any
from urllib.parse import quote

import requests
import yaml


ROOT = Path(__file__).resolve().parents[1]
SYNC_DIR = ROOT / ".notion-sync"
CONFIG_PATH = SYNC_DIR / "sources.json"
MANIFEST_PATH = SYNC_DIR / "manifest.json"

TOKEN = os.environ.get("NOTION_API_TOKEN", "").strip()
DATABASE_ID = os.environ.get("NOTION_DATABASE_ID", "").strip()
DATA_SOURCE_ID = os.environ.get("NOTION_DATA_SOURCE_ID", "").strip()
NOTION_VERSION = os.environ.get("NOTION_VERSION", "2026-03-11")
GITHUB_REPOSITORY = os.environ.get("GITHUB_REPOSITORY", "cookkie03/skills")
GITHUB_BRANCH = os.environ.get("GITHUB_REF_NAME", "main")
API_ROOT = "https://api.notion.com/v1"
MANAGED_PREFIX = "github-skills:"
MAX_ARCHIVE_BYTES = 20 * 1024 * 1024
EXCLUDED_ROOTS = {
    ".git", ".github", ".notion-sync", ".venv", "node_modules",
    "__pycache__", "third_party", "vendor", "dist", "build",
}


def fail(message: str) -> None:
    raise RuntimeError(message)


if not TOKEN:
    fail("Missing NOTION_API_TOKEN repository secret.")
if not DATABASE_ID or not DATA_SOURCE_ID:
    fail("Missing NOTION_DATABASE_ID or NOTION_DATA_SOURCE_ID.")


session = requests.Session()
session.headers.update({
    "Authorization": f"Bearer {TOKEN}",
    "Notion-Version": NOTION_VERSION,
    "Content-Type": "application/json",
    "Accept": "application/json",
})
_last_request_at = 0.0


def api(method: str, path: str, **kwargs: Any) -> dict:
    global _last_request_at
    url = path if path.startswith("https://") else API_ROOT + path
    for attempt in range(7):
        delay = 0.34 - (time.monotonic() - _last_request_at)
        if delay > 0:
            time.sleep(delay)
        response = session.request(method, url, timeout=90, **kwargs)
        _last_request_at = time.monotonic()
        if response.status_code == 429:
            retry_after = float(response.headers.get("Retry-After", "2"))
            time.sleep(max(retry_after, 1.0))
            continue
        if response.status_code in {500, 502, 503, 504}:
            time.sleep(min(2 ** attempt, 20))
            continue
        if not response.ok:
            try:
                detail = response.json()
            except Exception:
                detail = response.text[:2000]
            fail(f"Notion API {method} {path} failed ({response.status_code}): {detail}")
        if not response.content:
            return {}
        return response.json()
    fail(f"Notion API {method} {path} failed after retries.")
    return {}


def rich_text_value(value: str) -> list[dict]:
    value = str(value or "")
    if not value:
        return []
    return [
        {"type": "text", "text": {"content": value[index:index + 1800]}}
        for index in range(0, len(value), 1800)
    ]


def property_rich_text(value: str) -> dict:
    return {"rich_text": rich_text_value(value)}


def plain_rich_text(properties: dict, name: str) -> str:
    value = properties.get(name, {})
    chunks = value.get("rich_text", []) if isinstance(value, dict) else []
    return "".join(
        chunk.get("plain_text") or chunk.get("text", {}).get("content", "")
        for chunk in chunks
    )


def file_upload(archive: bytes, filename: str) -> str:
    if len(archive) > MAX_ARCHIVE_BYTES:
        fail(
            f"{filename} is {len(archive):,} bytes, above Notion's 20 MiB "
            "single-part upload limit. Reduce or split the supporting files."
        )

    created = api(
        "POST",
        "/file_uploads",
        json={
            "mode": "single_part",
            "filename": filename,
            "content_type": "application/zip",
        },
    )
    upload_url = created.get("upload_url")
    upload_id = created.get("id")
    if not upload_url or not upload_id:
        fail(f"Notion did not return a usable file upload URL for {filename}.")

    upload_headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Notion-Version": NOTION_VERSION,
        "Accept": "application/json",
    }
    response = requests.post(
        upload_url,
        headers=upload_headers,
        files={"file": (filename, archive, "application/zip")},
        timeout=180,
    )
    if not response.ok:
        fail(
            f"Notion file upload failed for {filename} "
            f"({response.status_code}): {response.text[:2000]}"
        )
    try:
        result = response.json()
        if result.get("status") == "failed":
            fail(f"Notion rejected file upload {filename}: {result}")
    except ValueError:
        # Some upload responses are empty or non-JSON on success.
        pass
    return upload_id


def parse_skill(skill_file: Path) -> tuple[str, str, str]:
    raw = skill_file.read_text(encoding="utf-8")
    match = re.match(r"\A---\s*\r?\n(.*?)\r?\n---\s*(?:\r?\n)?", raw, re.DOTALL)
    metadata: dict = {}
    body = raw
    if match:
        try:
            metadata = yaml.safe_load(match.group(1)) or {}
        except yaml.YAMLError as exc:
            fail(f"Invalid YAML frontmatter in {skill_file}: {exc}")
        body = raw[match.end():]
    if not isinstance(metadata, dict):
        fail(f"Frontmatter in {skill_file} must be a YAML mapping.")

    name = str(metadata.get("name") or skill_file.parent.name).strip()
    description = str(metadata.get("description") or "").strip()
    if not name:
        fail(f"Skill has no name: {skill_file}")
    if len(name) > 2000:
        fail(f"Skill name is longer than Notion's title limit: {skill_file}")
    if len(description) > 2000:
        fail(f"Skill description exceeds Notion's 2,000-character text limit: {skill_file}")
    if not body.strip():
        body = ""

    return name, description, body.rstrip() + ("\n" if body.strip() else "")


def make_archive(skill_dir: Path) -> tuple[bytes | None, str]:
    support_files = []
    for path in sorted(skill_dir.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        relative = path.relative_to(skill_dir)
        if path.name == "SKILL.md" or path.name == ".DS_Store":
            continue
        if any(part in {".git", "__pycache__"} for part in relative.parts):
            continue
        support_files.append((path, relative.as_posix()))

    digest = hashlib.sha256()
    for path, relative in support_files:
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")

    files_hash = digest.hexdigest()
    if not support_files:
        return None, files_hash

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for path, relative in support_files:
            info = zipfile.ZipInfo(relative)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (path.stat().st_mode & 0xFFFF) << 16
            archive.writestr(info, path.read_bytes())
    return buffer.getvalue(), files_hash


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def build_entry(
    skill_file: Path,
    source_id: str,
    source_label: str,
    category: str,
) -> dict:
    skill_dir = skill_file.parent
    name, description, body = parse_skill(skill_file)
    archive, files_hash = make_archive(skill_dir)
    repo_path = skill_file.relative_to(ROOT).as_posix()
    # Folder name is the stable identity: moving a skill between categories
    # updates its page instead of creating a second page.
    sync_id = f"{MANAGED_PREFIX}{source_id}:{skill_dir.name}"
    github_url = (
        f"https://github.com/{GITHUB_REPOSITORY}/blob/"
        f"{quote(GITHUB_BRANCH, safe='')}/{quote(repo_path, safe='/')}"
    )

    metadata = {
        "name": name,
        "description": description,
        "source": source_label,
        "category": category,
        "path": repo_path,
        "github_url": github_url,
    }
    fingerprint = sha256(
        json.dumps(metadata, sort_keys=True, ensure_ascii=False).encode("utf-8")
        + body.encode("utf-8")
        + files_hash.encode("ascii")
    )

    return {
        "sync_id": sync_id,
        "name": name,
        "description": description,
        "body": body,
        "source": source_label,
        "category": category,
        "path": repo_path,
        "github_url": github_url,
        "archive": archive,
        "files_hash": files_hash,
        "fingerprint": fingerprint,
    }


def discover_skills() -> list[dict]:
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    entries: list[dict] = []

    # Personal skills are one directory deep at the repository root.
    for child in sorted(ROOT.iterdir()):
        if child.name in EXCLUDED_ROOTS or child.name.startswith("."):
            continue
        if child.is_dir() and (child / "SKILL.md").is_file():
            entries.append(build_entry(
                child / "SKILL.md",
                "local",
                "Personal",
                "Personal",
            ))

    # Third-party snapshots are constrained to explicit configured destinations.
    for source in config.get("sources", []):
        source_root = ROOT / source["destination"]
        if not source_root.exists():
            fail(f"Configured third-party snapshot is missing: {source['destination']}")
        found = sorted(source_root.rglob("SKILL.md"))
        if not found:
            fail(f"No skills found under configured source {source['id']}.")
        for skill_file in found:
            relative = skill_file.relative_to(source_root)
            category = relative.parts[0].replace("-", " ").title() if len(relative.parts) > 1 else "Third Party"
            entries.append(build_entry(
                skill_file,
                source["id"],
                source["label"],
                category,
            ))

    if not entries:
        fail("No skills discovered; refusing to sync or delete anything.")
    ids = [entry["sync_id"] for entry in entries]
    if len(ids) != len(set(ids)):
        duplicates = sorted({item for item in ids if ids.count(item) > 1})
        fail(f"Duplicate Skill folder identities found: {duplicates}")
    return entries


def query_all_pages() -> list[dict]:
    pages: list[dict] = []
    cursor = None
    while True:
        payload: dict = {"page_size": 100}
        if cursor:
            payload["start_cursor"] = cursor
        result = api("POST", f"/data_sources/{DATA_SOURCE_ID}/query", json=payload)
        pages.extend(result.get("results", []))
        if not result.get("has_more"):
            break
        cursor = result.get("next_cursor")
        if not cursor:
            break
    return pages


def ensure_schema() -> None:
    result = api("GET", f"/data_sources/{DATA_SOURCE_ID}")
    properties = result.get("properties", {})
    required = {
        "Name", "Description", "Files", "Sync ID",
        "Source", "Category", "Repository Path", "GitHub URL",
    }
    missing = sorted(required - set(properties))
    if missing:
        fail(
            "The Notion Skills database is missing required properties: "
            + ", ".join(missing)
            + ". Recheck the database schema."
        )


def notion_properties(entry: dict, files: list[dict] | None = None) -> dict:
    properties = {
        "Name": {"title": rich_text_value(entry["name"])},
        "Description": property_rich_text(entry["description"]),
        "Sync ID": property_rich_text(entry["sync_id"]),
        "Source": property_rich_text(entry["source"]),
        "Category": property_rich_text(entry["category"]),
        "Repository Path": property_rich_text(entry["path"]),
        "GitHub URL": {"url": entry["github_url"]},
    }
    if files is not None:
        properties["Files"] = {"files": files}
    return properties


def current_page_last_edited(page: dict) -> str:
    return str(page.get("last_edited_time") or "")


def get_page(page_id: str) -> dict:
    return api("GET", f"/pages/{page_id}")


def create_page(entry: dict) -> dict:
    file_values: list[dict] = []
    if entry["archive"] is not None:
        filename = f"{entry['sync_id'].split(':')[-1]}-supporting-files.zip"
        upload_id = file_upload(entry["archive"], filename)
        file_values.append({
            "type": "file_upload",
            "file_upload": {"id": upload_id},
            "name": filename,
        })

    created = api(
        "POST",
        "/pages",
        json={
            "parent": {"type": "data_source_id", "data_source_id": DATA_SOURCE_ID},
            "properties": notion_properties(entry, files=file_values),
        },
    )
    page_id = created["id"]
    api(
        "PATCH",
        f"/pages/{page_id}/markdown",
        json={
            "type": "replace_content",
            "replace_content": {"new_str": entry["body"]},
        },
    )
    return get_page(page_id)


def update_page(page_id: str, entry: dict, replace_files: bool) -> dict:
    file_values = None
    if replace_files:
        file_values = []
        if entry["archive"] is not None:
            filename = f"{entry['sync_id'].split(':')[-1]}-supporting-files.zip"
            upload_id = file_upload(entry["archive"], filename)
            file_values.append({
                "type": "file_upload",
                "file_upload": {"id": upload_id},
                "name": filename,
            })

    api(
        "PATCH",
        f"/pages/{page_id}",
        json={"properties": notion_properties(entry, files=file_values)},
    )
    api(
        "PATCH",
        f"/pages/{page_id}/markdown",
        json={
            "type": "replace_content",
            "replace_content": {"new_str": entry["body"]},
        },
    )
    return get_page(page_id)


def main() -> None:
    ensure_schema()
    entries = discover_skills()
    pages = query_all_pages()

    by_sync_id: dict[str, dict] = {}
    for page in pages:
        sync_id = plain_rich_text(page.get("properties", {}), "Sync ID")
        if not sync_id.startswith(MANAGED_PREFIX):
            continue
        if sync_id in by_sync_id:
            fail(
                f"Duplicate Notion pages have Sync ID {sync_id}: "
                f"{by_sync_id[sync_id]['id']} and {page['id']}"
            )
        by_sync_id[sync_id] = page

    try:
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError:
        manifest = {"version": 1, "skills": {}}
    except json.JSONDecodeError as exc:
        fail(f"Invalid sync manifest; refusing to continue: {exc}")

    previous = manifest.get("skills", {})
    next_manifest: dict[str, dict] = {}
    desired_ids = {entry["sync_id"] for entry in entries}

    created_count = 0
    updated_count = 0
    unchanged_count = 0

    for entry in entries:
        sync_id = entry["sync_id"]
        page = by_sync_id.get(sync_id)
        previous_state = previous.get(sync_id, {})
        if page is None:
            page = create_page(entry)
            created_count += 1
            print(f"Created: {entry['name']} [{entry['path']}]")
        else:
            page_id = page["id"]
            page_time = current_page_last_edited(page)
            was_edited_in_notion = (
                bool(previous_state.get("notion_last_edited_time"))
                and page_time != previous_state.get("notion_last_edited_time")
            )
            source_changed = entry["fingerprint"] != previous_state.get("fingerprint")
            needs_update = source_changed or was_edited_in_notion or not previous_state
            if needs_update:
                files_changed = (
                    not previous_state
                    or entry["files_hash"] != previous_state.get("files_hash")
                    or was_edited_in_notion
                )
                page = update_page(page_id, entry, replace_files=files_changed)
                updated_count += 1
                print(f"Updated: {entry['name']} [{entry['path']}]")
            else:
                unchanged_count += 1

        next_manifest[sync_id] = {
            "page_id": page["id"],
            "fingerprint": entry["fingerprint"],
            "files_hash": entry["files_hash"],
            "notion_last_edited_time": current_page_last_edited(page),
            "repository_path": entry["path"],
        }

    # Only pages created by this synchronizer are eligible for deletion.
    deleted_count = 0
    for sync_id, page in by_sync_id.items():
        if sync_id in desired_ids:
            continue
        api("PATCH", f"/pages/{page['id']}", json={"in_trash": True})
        deleted_count += 1
        print(f"Moved to Notion Trash: {sync_id}")

    manifest = {
        "version": 1,
        "database_id": DATABASE_ID,
        "data_source_id": DATA_SOURCE_ID,
        "skills": next_manifest,
        "last_sync_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(
        "Notion sync completed: "
        f"{len(entries)} skills; {created_count} created; "
        f"{updated_count} updated; {unchanged_count} unchanged; "
        f"{deleted_count} moved to Trash."
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
