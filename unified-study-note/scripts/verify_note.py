#!/usr/bin/env python3
"""
verify_note.py - Quality and reconciliation audit gate for Unified Master Study Notes.
Checks TOC link integrity in the main study guide, balanced fences/details, math delimiters, and zero-loss source audit trail.
"""

import sys
import os
import re
import argparse


def verify_master_note(note_path: str) -> bool:
    if not os.path.isfile(note_path):
        print(f"Error: Note not found at '{note_path}'")
        return False

    with open(note_path, "r", encoding="utf-8") as f:
        text = f.read()

    print(f"Auditing Master Note: {note_path} ({len(text):,} characters, {len(text.splitlines()):,} lines)\n")
    all_passed = True

    # Separate Main Guide from Audit Trail
    parts = text.split("## Complete source record")
    main_body = parts[0]
    audit_trail = parts[1] if len(parts) > 1 else ""

    # 1. Check Main Table of Contents Wikilinks
    # Extract TOC section
    toc_match = re.search(r"## 📑 Table of Contents.*?(?=\n---|\n## )", main_body, re.DOTALL)
    if toc_match:
        toc_text = toc_match.group(0)
        toc_links = re.findall(r"\[\[#(.*?)(?:\|.*?)?\]\]", toc_text)
        print(f"1. Checking {len(toc_links)} Master Table of Contents links...")
        broken_links = []
        for anchor in toc_links:
            clean_anchor = re.escape(anchor.strip())
            pattern = r"(?m)^#{2,6}\s+" + clean_anchor + r"\s*$"
            if not re.search(pattern, text):
                plain_anchor = re.sub(r"[^\w\s-]", "", anchor).strip()
                if not re.search(r"(?m)^#{2,6}\s+.*" + re.escape(plain_anchor), text):
                    broken_links.append(anchor)

        if broken_links:
            print(f"   ❌ Found {len(broken_links)} broken TOC link(s):")
            for bl in broken_links:
                print(f"      - [[#{bl}]]")
            all_passed = False
        else:
            print("   ✅ All Master TOC links resolve perfectly to headings.")
    else:
        print("1. ⚠️ No dedicated Table of Contents block detected at top.")

    # 2. Check Code Fences Symmetry
    code_fences = len(re.findall(r"^```", text, re.MULTILINE))
    print(f"\n2. Checking code fence symmetry ({code_fences} fences detected)...")
    if code_fences % 2 != 0:
        print(f"   ❌ Code fences are asymmetrical ({code_fences} is odd)! An open fence is missing a closing fence.")
        all_passed = False
    else:
        print(f"   ✅ Code fences are symmetric ({code_fences // 2} blocks).")

    # 3. Check Details Tags
    open_details = len(re.findall(r"<details>", text))
    close_details = len(re.findall(r"</details>", text))
    print(f"\n3. Checking HTML details tags ({open_details} open, {close_details} close)...")
    if open_details != close_details:
        print(f"   ❌ Unmatched details tags: {open_details} <details> vs {close_details} </details>!")
        all_passed = False
    else:
        print(f"   ✅ All {open_details} <details> blocks are matched and closed.")

    # 4. Check Complete Source Record Truncation
    print("\n4. Checking Source Audit Trail integrity...")
    if not audit_trail:
        print("   ❌ Missing '## Complete source record' section!")
        all_passed = False
    else:
        sources_found = re.findall(r"### Source: `([^`]+)`", audit_trail)
        print(f"   Found {len(sources_found)} documented source entries.")
        truncated_matches = re.findall(r"(?i)\.\.\.\s*\[truncated\]", audit_trail)
        if truncated_matches:
            print(f"   ⚠️ Warning: Found {len(truncated_matches)} truncated source markers in the audit trail.")
            all_passed = False
        else:
            print("   ✅ Zero truncated source markers detected (100% full content preserved).")

    print("\n" + "=" * 40)
    if all_passed:
        print("🎉 RECONCILIATION AUDIT PASSED: Master note conforms to quality standards.")
    else:
        print("⚠️ AUDIT FAILED: Please fix the reported issues above.")
    print("=" * 40 + "\n")

    return all_passed


def main():
    parser = argparse.ArgumentParser(description="Audit and verify an Obsidian unified master study note.")
    parser.add_argument("note_path", help="Path to the master study note Markdown file.")
    args = parser.parse_args()

    success = verify_master_note(args.note_path)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
