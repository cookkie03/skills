#!/usr/bin/env python3
"""
extract_slides.py - Extract slide-by-slide text from PDF decks into persistent Markdown extracts.
Zero information loss pre-extraction for unified study notes.
"""

import sys
import os
import argparse

try:
    import pypdf
except ImportError:
    pypdf = None


def extract_pdf(pdf_path: str, output_path: str = None) -> str:
    if pypdf is None:
        raise ImportError("pypdf is required. Install with: pip install pypdf")

    if not os.path.isfile(pdf_path):
        raise FileNotFoundError(f"File not found: {pdf_path}")

    if output_path is None:
        base, _ = os.path.splitext(pdf_path)
        output_path = f"{base}_text_extract.md"

    reader = pypdf.PdfReader(pdf_path)
    total_pages = len(reader.pages)
    deck_name = os.path.basename(pdf_path)

    lines = [f"# Slide Text Extract: {deck_name}\n"]
    for idx, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        lines.append(f"## Slide {idx + 1}\n\n{text.strip()}\n")

    content = "\n".join(lines)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Extracted {total_pages} slides from '{deck_name}' -> '{output_path}'")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Extract slide text from PDF files to markdown.")
    parser.add_argument("target", help="Path to PDF file or directory containing PDF files.")
    parser.add_argument("-o", "--output", help="Optional explicit output markdown path (for single file).", default=None)
    args = parser.parse_args()

    if os.path.isfile(args.target) and args.target.lower().endswith(".pdf"):
        extract_pdf(args.target, args.output)
    elif os.path.isdir(args.target):
        found = False
        for root, _, files in os.walk(args.target):
            for file in files:
                if file.lower().endswith(".pdf") and not file.startswith("."):
                    pdf_path = os.path.join(root, file)
                    extract_pdf(pdf_path)
                    found = True
        if not found:
            print(f"No PDF files found in {args.target}")
    else:
        print(f"Invalid target: {args.target}. Must be a PDF file or directory.")
        sys.exit(1)


if __name__ == "__main__":
    main()
