#!/usr/bin/env python3
"""
update_source_record.py
Mechanically appends / updates the '## Complete source record' section
in the Master Note by reading output from diff_sources.py --json.

Usage:
  python3 scripts/update_source_record.py <course_dir> <note_path>
  python3 scripts/update_source_record.py <course_dir> <note_path> --force-include "Week4"

The script:
  1. Runs diff_sources.py --json internally to get the full source manifest.
  2. Reads the master note and strips any existing '## Complete source record' block.
  3. Rebuilds the block with ALL known sources (already ingested + new) with SHA-256 and type.
  4. Appends it back at the end of the master note.
"""

import os
import sys
import json
import hashlib
import argparse
import subprocess

SECTION_HEADER = "## Complete source record"

TYPE_MAP = {
    ".pdf": "Slide Deck Extract",
    ".m4a": "Audio Transcript",
    ".mp3": "Audio Transcript",
    ".ipynb": "Native Code Notebook",
    ".md": "Markdown / Workbook",
    ".txt": "Plain Text",
    ".r": "R Script",
    ".py": "Python Script",
}


def sha256_of_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def run_diff_sources(course_dir, note_path, force_include=None):
    script = os.path.join(os.path.dirname(__file__), "diff_sources.py")
    cmd = [sys.executable, script, course_dir, note_path, "--json"]
    if force_include:
        cmd += ["--force-include", force_include]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running diff_sources.py:\n{result.stderr}", file=sys.stderr)
        sys.exit(1)
    return json.loads(result.stdout)


def build_record_block(diff_result, course_dir):
    all_sources = (
        diff_result.get("new_sources", [])
        + diff_result.get("already_processed", [])
        + diff_result.get("modified_sources", [])
    )
    if not all_sources:
        return f"{SECTION_HEADER}\n\n*(No sources found)*\n"

    lines = [SECTION_HEADER, ""]
    for entry in sorted(all_sources, key=lambda e: e.get("relative_path", "")):
        rel_path = entry.get("relative_path", "")
        sha = entry.get("sha256", "")
        ext = os.path.splitext(rel_path)[1].lower()
        file_type = TYPE_MAP.get(ext, "Unknown")

        # Recompute sha if missing
        if not sha:
            full_path = os.path.join(course_dir, rel_path)
            if os.path.exists(full_path):
                sha = sha256_of_file(full_path)

        lines.append(f"### Source: `{rel_path}`")
        lines.append(f"- **SHA256**: `{sha}`")
        lines.append(f"- **Type**: {file_type}")
        lines.append("")

    return "\n".join(lines)


def update_master_note(note_path, record_block):
    with open(note_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Strip existing Complete source record section (everything after it)
    if SECTION_HEADER in content:
        content = content[: content.index(SECTION_HEADER)].rstrip()

    updated = content + "\n\n---\n\n" + record_block + "\n"
    with open(note_path, "w", encoding="utf-8") as f:
        f.write(updated)


def main():
    parser = argparse.ArgumentParser(
        description="Mechanically rebuild the '## Complete source record' in the Master Note."
    )
    parser.add_argument("course_dir", help="Course root directory")
    parser.add_argument("note_path", help="Path to the Master Note .md file")
    parser.add_argument(
        "--force-include",
        default=None,
        help="Regex pattern to force-include already-ingested files",
    )
    args = parser.parse_args()

    print("Running diff_sources.py to collect full manifest...")
    diff = run_diff_sources(args.course_dir, args.note_path, args.force_include)

    new_count = len(diff.get("new_sources", []))
    already_count = len(diff.get("already_processed", []))
    modified_count = len(diff.get("modified_sources", []))
    total = new_count + already_count + modified_count
    print(f"  Found {total} total sources ({new_count} new, {modified_count} modified, {already_count} already ingested)")

    record_block = build_record_block(diff, args.course_dir)
    update_master_note(args.note_path, record_block)

    print(f"✅ Source record updated in {args.note_path}")


if __name__ == "__main__":
    main()
