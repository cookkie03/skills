#!/usr/bin/env python3
"""
verify_note.py - Quality and reconciliation audit gate for Unified Master Study Notes.
Checks TOC link integrity, balanced fences, matching HTML details tags, and syntax standards.
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

    # 1. Check Table of Contents Wikilinks
    toc_match = re.search(r"## 📑 Table of Contents.*?(?=\n---|\n## )", text, re.DOTALL)
    if toc_match:
        toc_text = toc_match.group(0)
        toc_links = re.findall(r"\[\[#(.*?)(?:\|.*?)?\]\]", toc_text)
        print(f"1. Checking {len(toc_links)} Table of Contents links...")
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
            print("   ✅ All TOC links resolve perfectly to headings.")
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

    # 3. Check Details Tags (if any exist)
    open_details = len(re.findall(r"<details>", text))
    close_details = len(re.findall(r"</details>", text))
    if open_details > 0 or close_details > 0:
        print(f"\n3. Checking HTML details tags ({open_details} open, {close_details} close)...")
        if open_details != close_details:
            print(f"   ❌ Unmatched details tags: {open_details} <details> vs {close_details} </details>!")
            all_passed = False
        else:
            print(f"   ✅ All {open_details} <details> blocks are matched and closed.")
    else:
        print("\n3. HTML details tags check: None present.")

    # 4. Check LaTeX and Math Delimiters Symmetry
    double_dollars = len(re.findall(r"\$\$", text))
    if double_dollars % 2 != 0:
        print(f"\n4. ❌ Asymmetric display math delimiters ($$ count: {double_dollars})!")
        all_passed = False
    else:
        print(f"\n4. ✅ Display math delimiters symmetric ({double_dollars // 2} display equations).")

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
