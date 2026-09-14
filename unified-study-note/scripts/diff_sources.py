#!/usr/bin/env python3
"""
diff_sources.py - Zero-token deterministic source diffing tool with SHA-256 hash tracking.
Compares files in a course directory against the Master Note's source manifest:
- '## Complete source record'
- '## Synchronized Course Assets & Inventory'
- '## Synchronized Canvas Assets'
- '## Sources'

Detects new, modified, and already-ingested sources to prevent redundant processing and LLM token waste.
"""

import os
import sys
import re
import json
import hashlib
import argparse
from typing import List, Dict, Set, Tuple


SUPPORTED_EXTENSIONS = {
    "slides": {".pdf", ".pptx"},
    "audio": {".m4a", ".mp3", ".wav", ".aac", ".webm", ".ogg"},
    "code": {".r", ".py", ".ipynb", ".sql"},
    "docs": {".docx", ".doc", ".txt"}
}

ALL_EXTENSIONS = set().union(*SUPPORTED_EXTENSIONS.values())

IGNORED_PATTERNS = [
    r"\.staging.*",
    r"\.git.*",
    r"^images$",
    r".*_extract\.md$",
    r".*_transcript\.md$",
    r"^\..*"
]

MANIFEST_SECTION_PATTERNS = [
    r"## Complete source record.*",
    r"## Synchronized Course Assets.*",
    r"## Synchronized Canvas Assets.*",
    r"## Course Assets.*",
    r"## Sources.*"
]


def is_ignored(path: str) -> bool:
    name = os.path.basename(path)
    for pattern in IGNORED_PATTERNS:
        if re.match(pattern, name, re.IGNORECASE):
            return True
    return False


def get_category(ext: str) -> str:
    ext_lower = ext.lower()
    for cat, exts in SUPPORTED_EXTENSIONS.items():
        if ext_lower in exts:
            return cat
    return "other"


def compute_sha256(file_path: str) -> str:
    h = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return ""


def extract_processed_manifest_from_note(note_path: str) -> Tuple[Dict[str, str], Set[str]]:
    """
    Returns:
        name_to_hash: {filename.lower(): hash_if_present}
        hashes_set: {sha256_hash}
    """
    name_to_hash = {}
    hashes_set = set()

    if not os.path.isfile(note_path):
        return name_to_hash, hashes_set

    with open(note_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # Find the manifest section
    search_text = ""
    for pat in MANIFEST_SECTION_PATTERNS:
        m = re.search(pat, content, re.DOTALL | re.IGNORECASE)
        if m:
            search_text = m.group(0)
            break

    if not search_text:
        search_text = content

    # 1. Matches: ### Source: `filename` (SHA256: `hash`)
    entries = re.split(r"(?m)^###\s+Source:\s*", search_text)
    for entry in entries[1:]:
        header_line = entry.splitlines()[0]
        name_m = re.search(r"`?([^`\n\r(]+)`?", header_line)
        if name_m:
            fn = os.path.basename(name_m.group(1).strip()).lower()
            top_lines = "\n".join(entry.splitlines()[:5])
            hash_m = re.search(r"(?:SHA256|sha256|hash):\s*`?([a-fA-F0-9]{64})`?", top_lines)
            entry_hash = hash_m.group(1).lower() if hash_m else ""
            name_to_hash[fn] = entry_hash
            if entry_hash:
                hashes_set.add(entry_hash)

    # 2. Matches filenames inside backticks: `Modules/.../Lecture1.pdf` or `Lecture1.pdf`
    for m in re.finditer(r"`([^`\n\r]+?\.(?:pdf|pptx|m4a|mp3|wav|aac|webm|ogg|r|py|ipynb|sql|docx|txt))`", search_text, re.IGNORECASE):
        raw_path = m.group(1).strip()
        # Handle cases like `data.csv`, `Week1.ipynb`
        for part in raw_path.split(","):
            cleaned = os.path.basename(part.strip().strip("'\"")).lower()
            if cleaned:
                name_to_hash[cleaned] = name_to_hash.get(cleaned, "")

    # 3. Matches filenames in markdown bullets: - Materials/.../file.pdf
    for m in re.finditer(r"(?m)^\s*[-*]\s+(?:`?)([^`\n\r]+?\.(?:pdf|pptx|m4a|mp3|wav|aac|webm|ogg|r|py|ipynb|sql|docx|txt))(?:`?)", search_text, re.IGNORECASE):
        raw_path = m.group(1).strip()
        cleaned = os.path.basename(raw_path.strip().strip("'\"")).lower()
        if cleaned:
            name_to_hash[cleaned] = name_to_hash.get(cleaned, "")

    # 4. Matches wikilinks: [[filename.pdf]]
    for m in re.finditer(r"\[\[([^\]|#]+?\.(?:pdf|pptx|m4a|mp3|wav|aac|webm|ogg|r|py|ipynb|sql|docx|txt))(?:\|[^\]]+)?\]\]", search_text, re.IGNORECASE):
        src = os.path.basename(m.group(1).strip()).lower()
        if src not in name_to_hash:
            name_to_hash[src] = ""

    return name_to_hash, hashes_set


def diff_sources(course_dir: str, note_path: str = None) -> Dict:
    course_dir = os.path.abspath(course_dir)
    if not os.path.isdir(course_dir):
        raise FileNotFoundError(f"Course directory not found: {course_dir}")

    # Determine master note path if not specified
    if not note_path:
        course_name = os.path.basename(course_dir)
        candidate = os.path.join(course_dir, f"{course_name}.md")
        if os.path.isfile(candidate):
            note_path = candidate
        else:
            for f in os.listdir(course_dir):
                if f.endswith(".md") and not is_ignored(f):
                    note_path = os.path.join(course_dir, f)
                    break

    name_to_hash, hashes_set = extract_processed_manifest_from_note(note_path) if note_path else ({}, set())

    new_sources = []
    modified_sources = []
    already_processed = []

    for root, dirs, files in os.walk(course_dir):
        dirs[:] = [d for d in dirs if not is_ignored(d)]

        for f in sorted(files):
            if is_ignored(f):
                continue

            _, ext = os.path.splitext(f)
            if ext.lower() not in ALL_EXTENSIONS:
                continue

            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(full_path, course_dir)
            f_lower = f.lower()
            file_hash = compute_sha256(full_path)

            item = {
                "file_name": f,
                "relative_path": rel_path,
                "absolute_path": full_path,
                "category": get_category(ext),
                "extension": ext.lower(),
                "sha256": file_hash
            }

            if file_hash and file_hash in hashes_set:
                already_processed.append(item)
            elif f_lower in name_to_hash:
                recorded_hash = name_to_hash[f_lower]
                if recorded_hash and file_hash and recorded_hash != file_hash:
                    item["recorded_sha256"] = recorded_hash
                    modified_sources.append(item)
                else:
                    already_processed.append(item)
            else:
                new_sources.append(item)

    return {
        "course_dir": course_dir,
        "master_note_path": note_path,
        "master_note_exists": os.path.isfile(note_path) if note_path else False,
        "total_course_sources": len(new_sources) + len(modified_sources) + len(already_processed),
        "total_new": len(new_sources),
        "total_modified": len(modified_sources),
        "total_already_processed": len(already_processed),
        "new_sources": new_sources,
        "modified_sources": modified_sources,
        "already_processed": already_processed
    }


def main():
    parser = argparse.ArgumentParser(description="Deterministic diff tool for course materials vs Master Note.")
    parser.add_argument("course_dir", help="Directory containing the course files.")
    parser.add_argument("note_path", nargs="?", default=None, help="Optional explicit path to the Master Note .md file.")
    parser.add_argument("--json", action="store_true", help="Output raw JSON only.")
    args = parser.parse_args()

    try:
        res = diff_sources(args.course_dir, args.note_path)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(res, indent=2))
        return

    print("=" * 60)
    print("📊 DETERMINISTIC COURSE SOURCE DIFF REPORT")
    print("=" * 60)
    print(f"Course Dir:   {res['course_dir']}")
    print(f"Master Note:  {res['master_note_path']} (Exists: {res['master_note_exists']})")
    print(f"Total Sources: {res['total_course_sources']}")
    print(f"Already Ingested: {res['total_already_processed']}")
    print(f"Modified Sources: {res['total_modified']}")
    print(f"New Sources To Process: {res['total_new']}")
    print("-" * 60)

    if res['new_sources'] or res['modified_sources']:
        if res['new_sources']:
            print("\n✨ NEW SOURCES TO PROCESS:")
            for s in res['new_sources']:
                print(f"  • [{s['category'].upper()}] {s['relative_path']} (sha256: {s['sha256'][:10]}...)")
        if res['modified_sources']:
            print("\n🔄 MODIFIED SOURCES (Hash changed):")
            for s in res['modified_sources']:
                print(f"  • [{s['category'].upper()}] {s['relative_path']}")
    else:
        print("\n✅ All sources are already fully ingested into the Master Note.")

    print("=" * 60)


if __name__ == "__main__":
    main()
