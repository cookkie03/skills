#!/usr/bin/env python3
"""Refresh configured third-party skill snapshots without touching other repo paths."""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / ".notion-sync" / "sources.json"
MANIFEST = ROOT / ".notion-sync" / "upstreams-manifest.json"


def run(command: list[str]) -> None:
    subprocess.run(command, check=True)


def find_skill_file(skill_dir: Path) -> Path | None:
    if not skill_dir.is_dir() or skill_dir.is_symlink():
        return None
    for item in sorted(skill_dir.iterdir()):
        if item.is_file() and not item.is_symlink() and item.name.casefold() == "skill.md":
            return item
    return None


def copy_skill_tree(source_dir: Path, target_dir: Path) -> None:
    target_dir.mkdir(parents=True, exist_ok=True)
    for item in source_dir.rglob("*"):
        if item.is_symlink():
            continue
        relative = item.relative_to(source_dir)
        if any(part in {".git", "__pycache__"} for part in relative.parts):
            continue
        if item.name == ".DS_Store":
            continue
        destination = target_dir / relative
        if item.is_dir():
            destination.mkdir(parents=True, exist_ok=True)
        elif item.is_file():
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, destination)


def extract_locality_skill(checkout: Path, source: dict, stage: Path) -> int:
    source_file = checkout / source["extractor_file"]
    if not source_file.is_file():
        raise RuntimeError(f"{source['id']}: Locality skill generator not found: {source_file}")

    rust = source_file.read_text(encoding="utf-8")
    skill_match = re.search(
        r'fn skill_markdown\(mount_path: &str\) -> String\s*\{\s*'
        r'format!\(\s*r#"(.*?)"#,\s*suggested_agent_prompt\(mount_path\)\s*\)',
        rust,
        re.DOTALL,
    )
    prompt_match = re.search(
        r'fn suggested_agent_prompt\(mount_path: &str\) -> String\s*\{\s*'
        r'format!\(\s*"([^"]*)"\s*\)',
        rust,
        re.DOTALL,
    )
    if not skill_match or not prompt_match:
        raise RuntimeError(
            f"{source['id']}: could not safely extract the generated Locality skill."
        )

    mount_path = source["mount_path"]
    prompt = prompt_match.group(1).replace("{mount_path}", mount_path)
    markdown = skill_match.group(1)
    markdown = markdown.replace("{{", "__LITERAL_LEFT_BRACE__")
    markdown = markdown.replace("}}", "__LITERAL_RIGHT_BRACE__")
    markdown = markdown.replace("{mount_path}", mount_path)
    if markdown.count("{}") != 1:
        raise RuntimeError(
            f"{source['id']}: unexpected Locality template placeholders; refusing stale output."
        )
    markdown = markdown.replace("{}", prompt)
    markdown = markdown.replace("__LITERAL_LEFT_BRACE__", "{")
    markdown = markdown.replace("__LITERAL_RIGHT_BRACE__", "}")

    skill_dir = stage / source.get("skill_dir", "locality")
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(markdown.strip() + "\n", encoding="utf-8")
    print(f"{source['id']}: generated Locality skill from {source['extractor_file']}")
    return 1


def managed_destination(value: str) -> Path:
    """Resolve a configured mirror path and ensure it stays inside third_party/."""
    base = (ROOT / "third_party").resolve()
    target = (ROOT / value).resolve()
    try:
        relative = target.relative_to(base)
    except ValueError as exc:
        raise RuntimeError(
            f"Managed destination must be inside third_party/: {value}"
        ) from exc
    if not relative.parts:
        raise RuntimeError("A source cannot own the third_party/ root itself.")
    return target


def prune_excluded_skill_paths(stage: Path, source: dict) -> None:
    """Remove excluded skill directories from the snapshot before it reaches GitHub."""
    for raw_path in source.get("exclude_skill_paths", []):
        relative = Path(raw_path)
        if relative.is_absolute() or ".." in relative.parts:
            raise RuntimeError(
                f"{source['id']}: unsafe exclude_skill_paths entry: {raw_path}"
            )
        target = stage / relative
        if not target.exists():
            continue
        if target.is_dir():
            shutil.rmtree(target)
        elif target.name.casefold() == "skill.md":
            # Remove the complete excluded skill directory, not just its entrypoint.
            shutil.rmtree(target.parent)
        else:
            target.unlink()
        print(f"{source['id']}: excluded {relative.as_posix()}")


def sync_source(source: dict) -> int:
    repo_url = source["repo"]
    branch = source.get("branch", "main")
    includes = source["include"]
    path_prefix = Path(source.get("source_path_prefix", "."))
    destination = ROOT / source["destination"]
    source_id = source["id"]

    with tempfile.TemporaryDirectory(prefix="skills-upstream-") as temp:
        checkout = Path(temp) / "checkout"
        stage = Path(temp) / "stage"
        run([
            "git", "clone", "--depth", "1", "--filter=blob:none", "--sparse",
            "--single-branch", "--branch", branch, repo_url, str(checkout),
        ])
        run(["git", "-C", str(checkout), "sparse-checkout", "set", *includes])

        if source.get("extractor_type") == "locality_rust":
            count = extract_locality_skill(checkout, source, stage)
        else:
            count = 0
            for include in includes:
                include_path = checkout / include
                if not include_path.exists() or include_path.is_symlink():
                    continue

                # An include can be a skill directory itself, or a category whose
                # immediate children are skill directories.
                if find_skill_file(include_path):
                    candidates = [include_path]
                elif include_path.is_dir():
                    candidates = [
                        child for child in sorted(include_path.iterdir())
                        if find_skill_file(child)
                    ]
                else:
                    candidates = []

                for skill_dir in candidates:
                    if skill_dir == checkout:
                        relative = Path(source.get("root_skill_name") or
                                        Path(urlparse(repo_url).path).stem)
                    else:
                        try:
                            relative = skill_dir.relative_to(checkout / path_prefix)
                        except ValueError as exc:
                            raise RuntimeError(
                                f"{source_id}: skill path {skill_dir} is outside "
                                f"source_path_prefix {path_prefix}"
                            ) from exc
                    if relative == Path("."):
                        relative = Path(source.get("root_skill_name") or
                                        Path(urlparse(repo_url).path).stem)
                    copy_skill_tree(skill_dir, stage / relative)
                    count += 1

        prune_excluded_skill_paths(stage, source)
        staged_skill_files = [
            path for path in stage.rglob("*")
            if path.is_file() and path.name.casefold() == "skill.md"
        ]
        if count == 0 or not staged_skill_files:
            raise RuntimeError(
                f"{source_id}: no SKILL.md files found in configured paths; "
                "keeping the existing third-party snapshot untouched."
            )

        # Each configured destination is a dedicated upstream mirror. Replacing
        # only this directory propagates upstream moves/deletions without touching
        # personal skills or other third-party sources.
        if destination.exists():
            shutil.rmtree(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(stage, destination)

    print(
        f"{source_id}: refreshed {count} selected skill(s) into "
        f"{source['destination']} ({len(staged_skill_files)} SKILL.md file(s), "
        "including any upstream nested copies)."
    )
    return count


def main() -> None:
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    sources = config.get("sources", [])
    ids = [source["id"] for source in sources]
    destinations = [source["destination"] for source in sources]
    if len(ids) != len(set(ids)):
        raise RuntimeError("Duplicate upstream source IDs in sources.json.")
    if len(destinations) != len(set(destinations)):
        raise RuntimeError("Duplicate upstream destinations in sources.json.")

    current_destinations = {
        str(managed_destination(source["destination"]))
        for source in sources
    }
    # Do not allow nested mirrors: removing one must never remove another source.
    ordered_destinations = sorted(current_destinations)
    for index, destination in enumerate(ordered_destinations):
        for other in ordered_destinations[index + 1:]:
            if other.startswith(destination + "/"):
                raise RuntimeError(
                    f"Overlapping upstream destinations are not allowed: "
                    f"{destination} and {other}"
                )

    previous = {}
    if MANIFEST.is_file():
        previous_data = json.loads(MANIFEST.read_text(encoding="utf-8"))
        previous = {
            item["id"]: item["destination"]
            for item in previous_data.get("sources", [])
        }

    # Refresh every configured source first. A failure preserves old mirrors and
    # the previous manifest, so the Notion sync cannot interpret a partial run
    # as intentional deletion.
    total = 0
    for source in sources:
        total += sync_source(source)

    for source_id, old_destination in previous.items():
        old_path = managed_destination(old_destination)
        old_resolved = str(old_path)
        if old_resolved in current_destinations:
            continue
        for active_destination in current_destinations:
            if (
                active_destination.startswith(old_resolved + "/")
                or old_resolved.startswith(active_destination + "/")
            ):
                raise RuntimeError(
                    "An old mirror overlaps a currently configured destination. "
                    "Move the destination manually before syncing: "
                    f"{old_destination} vs {active_destination}"
                )
        if old_path.exists():
            shutil.rmtree(old_path)
            print(
                f"Removed upstream mirror no longer configured: "
                f"{source_id} -> {old_destination}"
            )

    manifest = {
        "version": 1,
        "sources": [
            {
                "id": source["id"],
                "repo": source["repo"],
                "branch": source.get("branch", "main"),
                "destination": source["destination"],
            }
            for source in sources
        ],
    }
    MANIFEST.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(
        f"Third-party refresh complete: {total} selected skills "
        f"across {len(sources)} sources."
    )


if __name__ == "__main__":
    main()
