#!/usr/bin/env python3
"""
Zero-Token Lecture Slide Scratchpad Generator
Usage:
    python3 generate_scratchpad.py --pdf "/path/to/slides.pdf" --output "/path/to/Week N - Personal Notes.md"
"""

import argparse
import datetime
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


def find_binary(name):
    """Find a binary in PATH or common Aside / system locations."""
    path = shutil.which(name)
    if path:
        return path
    candidates = [
        f"/Users/luca/.aside/runtime/bin/{name}",
        f"/opt/homebrew/bin/{name}",
        f"/usr/local/bin/{name}",
        f"/usr/bin/{name}",
    ]
    for c in candidates:
        if os.path.isfile(c) and os.access(c, os.X_OK):
            return c
    return None


def extract_slide_texts(pdf_path, pdftotext_bin):
    """Extract per-slide raw text using pdftotext."""
    cmd = [pdftotext_bin, str(pdf_path), "-"]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        pages = res.stdout.split("\x0c")
        if pages and not pages[-1].strip():
            pages = pages[:-1]
        return pages
    except Exception as e:
        print(f"Warning: pdftotext failed: {e}", file=sys.stderr)
        return []


def clean_slide_title(page_text, slide_index):
    """Extract a clean, concise slide title from the top text lines of a slide."""
    lines = [l.strip() for l in page_text.splitlines() if l.strip()]
    if not lines:
        return f"Slide {slide_index:02d}"

    # Filter out pure noise lines (page numbers, standalone symbols, dates)
    cleaned = []
    for line in lines:
        # Ignore standalone slide numbers or date stamps
        if re.match(r"^\d+$", line) or re.match(r"^\d{1,2}/\d{1,2}/\d{2,4}$", line):
            continue
        if re.match(r"^[•\-\*\.\|]+$", line):
            continue
        cleaned.append(line)

    if not cleaned:
        return f"Slide {slide_index:02d}"

    # Take first meaningful line, strip extra bullets or numbering
    title = cleaned[0]
    title = re.sub(r"^[•\-\*\d\.\)\s]+", "", title).strip()
    
    # If first line was very short, try appending second line if it fits
    if len(title) < 15 and len(cleaned) > 1:
        second = re.sub(r"^[•\-\*\d\.\)\s]+", "", cleaned[1]).strip()
        if second and len(f"{title} - {second}") <= 60:
            title = f"{title} - {second}"

    # Limit title length
    if len(title) > 70:
        title = title[:67] + "..."

    return title if title else f"Slide {slide_index:02d}"


def get_vault_relative_path(target_path, note_path):
    """Determine the relative vault link path for an image."""
    target = Path(target_path).resolve()
    
    # Common vault anchors
    vault_markers = ["Second-Brain", "Documents/Second-Brain"]
    for marker in vault_markers:
        target_str = str(target)
        if marker in target_str:
            idx = target_str.find(marker)
            rel = target_str[idx + len(marker):].lstrip("/")
            return rel
            
    # Fallback: relative to note parent
    try:
        note_parent = Path(note_path).resolve().parent
        return str(target.relative_to(note_parent))
    except Exception:
        return target.name


def main():
    parser = argparse.ArgumentParser(
        description="Zero-token generation of Obsidian slide scratchpad notes."
    )
    parser.add_argument("--pdf", "-p", required=True, help="Path to lecture slides PDF")
    parser.add_argument("--output", "-o", required=True, help="Output markdown note path")
    parser.add_argument("--images-dir", "-i", help="Directory to save rendered slide PNGs")
    parser.add_argument("--dpi", type=int, default=150, help="DPI for slide rendering (default: 150)")
    parser.add_argument("--title", help="Custom note title")
    parser.add_argument("--course", help="Course name (auto-detected from path if omitted)")
    parser.add_argument("--lecture", help="Lecture or Week label (e.g. 'Week 3')")
    parser.add_argument("--force", "-f", action="store_true", help="Overwrite existing output note")

    args = parser.parse_args()

    pdf_path = Path(args.pdf).resolve()
    if not pdf_path.is_file():
        print(f"Error: Slide PDF not found at '{pdf_path}'", file=sys.stderr)
        sys.exit(1)

    output_path = Path(args.output).resolve()
    if output_path.exists() and not args.force:
        print(f"Error: Output file already exists at '{output_path}'. Use --force to overwrite.", file=sys.stderr)
        sys.exit(1)

    # Locate required binaries
    pdftoppm_bin = find_binary("pdftoppm")
    pdftotext_bin = find_binary("pdftotext")

    if not pdftoppm_bin:
        print("Error: pdftoppm binary not found. Please install poppler utilities.", file=sys.stderr)
        sys.exit(1)

    # Determine images directory
    if args.images_dir:
        images_dir = Path(args.images_dir).resolve()
    else:
        # Check if PDF is in a Module folder with an images/ subfolder
        pdf_parent = pdf_path.parent
        images_dir = pdf_parent / "images"

    images_dir.mkdir(parents=True, exist_ok=True)

    # 1. Render slides to PNG
    print(f"Rendering slides from '{pdf_path.name}' at {args.dpi} DPI to '{images_dir}'...")
    ppm_prefix = images_dir / "slide"
    cmd_render = [pdftoppm_bin, "-png", "-r", str(args.dpi), str(pdf_path), str(ppm_prefix)]
    subprocess.run(cmd_render, check=True)

    # Make images readable
    for img in images_dir.glob("slide-*.png"):
        os.chmod(img, 0o644)

    # 2. Extract slide texts & count
    slide_texts = []
    if pdftotext_bin:
        slide_texts = extract_slide_texts(pdf_path, pdftotext_bin)

    rendered_images = sorted(list(images_dir.glob("slide-*.png")))
    num_slides = len(rendered_images)
    if num_slides == 0:
        print("Error: No slide images were rendered.", file=sys.stderr)
        sys.exit(1)

    print(f"Successfully processed {num_slides} slides.")

    # 3. Infer metadata
    course_name = args.course
    if not course_name:
        parts = output_path.parts
        if "tilburg-university" in parts:
            idx = parts.index("tilburg-university")
            if idx + 1 < len(parts):
                course_name = parts[idx + 1]
        if not course_name:
            course_name = output_path.parent.name

    lecture_label = args.lecture
    if not lecture_label:
        match = re.search(r"(Week\s*\d+|Lecture\s*\d+)", output_path.name, re.IGNORECASE)
        if match:
            lecture_label = match.group(1).title()
        else:
            lecture_label = "Lecture"

    note_title = args.title or f"{lecture_label} — Personal Notes"
    current_date = datetime.date.today().isoformat()

    # 4. Generate Markdown
    md_lines = []
    md_lines.append("---")
    md_lines.append(f'course: "{course_name}"')
    md_lines.append(f'lecture: "{lecture_label}"')
    md_lines.append(f'date: "{current_date}"')
    md_lines.append('type: "Personal Scratchpad Notes"')
    md_lines.append("tags:")
    md_lines.append("  - scratchpad")
    md_lines.append("  - lecture-notes")
    md_lines.append("---")
    md_lines.append("")
    md_lines.append(f"# {note_title}")
    md_lines.append("")
    md_lines.append(f"> **Course**: {course_name}  ")
    md_lines.append(f"> **Slide Deck**: `{pdf_path.name}` ({num_slides} Slides)  ")
    md_lines.append(f"> **Date**: {current_date}  ")
    md_lines.append("")
    md_lines.append("---")
    md_lines.append("")

    for i in range(1, num_slides + 1):
        img_name = f"slide-{i:02d}.png"
        img_path = images_dir / img_name
        rel_img_path = get_vault_relative_path(img_path, output_path)

        page_text = slide_texts[i - 1] if i - 1 < len(slide_texts) else ""
        slide_title = clean_slide_title(page_text, i)

        md_lines.append(f"#### Slide {i:02d}: {slide_title}")
        md_lines.append(f"![[{rel_img_path}]]")
        md_lines.append("")
        md_lines.append("### Spoken Lecture Takeaways & Audio Insights")
        md_lines.append("- ")
        md_lines.append("")
        md_lines.append("### Questions & Clarifications")
        md_lines.append("- ")
        md_lines.append("")
        md_lines.append("---")
        md_lines.append("")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    print(f"Scratchpad successfully generated at: {output_path}")


if __name__ == "__main__":
    main()
