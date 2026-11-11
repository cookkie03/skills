#!/usr/bin/env python3
"""
Zero-Token Lecture Slide Scratchpad Generator

Renders PDF slide decks to images and generates clean, structured Obsidian
scratchpad notes with blank worksheets for real-time in-class note taking.
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
        f"/bin/{name}",
    ]
    for c in candidates:
        if os.path.isfile(c) and os.access(c, os.X_OK):
            return c
    return None


def natural_sort_key(path):
    """Extract numeric index from path for natural sorting."""
    match = re.search(r"(\d+)", path.stem)
    return int(match.group(1)) if match else 0


def extract_slide_texts(pdf_path, pdftotext_bin=None):
    """Extract per-slide raw text using pdftotext."""
    if not pdftotext_bin:
        pdftotext_bin = find_binary("pdftotext")
    if not pdftotext_bin:
        return []

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

    cleaned = []
    for line in lines:
        # Ignore standalone slide/page numbers or dates
        if re.match(r"^\d+$", line) or re.match(r"^Slide\s*\d+$", line, re.IGNORECASE):
            continue
        if re.match(r"^\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4}$", line):
            continue
        if re.match(r"^[•\-\*\.\|\s]+$", line):
            continue
        # Strip noisy leading bullets, punctuation, numbers
        stripped = re.sub(r"^[•\-\*\d\.\)\:\s]+", "", line).strip()
        stripped = stripped.lstrip(" -:•*|").strip()
        if stripped:
            cleaned.append(stripped)

    if not cleaned:
        return f"Slide {slide_index:02d}"

    title = cleaned[0]

    # If first line was very short, try appending second line if it fits
    if len(title) < 15 and len(cleaned) > 1:
        second = cleaned[1]
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


def infer_metadata(pdf_path, output_path, course=None, lecture=None, title=None):
    """Infer course name, lecture label, and note title from file paths."""
    out_path = Path(output_path).resolve()
    pdf_p = Path(pdf_path).resolve()

    course_name = course
    if not course_name:
        parts = out_path.parts
        if "tilburg-university" in parts:
            idx = parts.index("tilburg-university")
            if idx + 1 < len(parts):
                course_name = parts[idx + 1]
        elif "Second-Brain" in parts:
            idx = parts.index("Second-Brain")
            if idx + 2 < len(parts):
                course_name = parts[idx + 2]
        if not course_name:
            course_name = out_path.parent.name

    lecture_label = lecture
    if not lecture_label:
        match = re.search(r"(Week\s*\d+|Lecture\s*\d+|Module\s*\d+)", out_path.name, re.IGNORECASE)
        if not match:
            match = re.search(r"(Week\s*\d+|Lecture\s*\d+|Module\s*\d+)", pdf_p.name, re.IGNORECASE)
        if match:
            lecture_label = match.group(1).title()
        else:
            lecture_label = "Lecture"

    note_title = title or f"{lecture_label} — Personal Notes"

    return {
        "course": course_name,
        "lecture": lecture_label,
        "title": note_title,
    }


def build_scratchpad_markdown(
    course_name,
    lecture_label,
    note_title,
    pdf_name,
    num_slides,
    slide_items,
    date_str=None,
):
    """Build the complete Obsidian markdown string for a scratchpad note."""
    current_date = date_str or datetime.date.today().isoformat()

    lines = [
        "---",
        f'course: "{course_name}"',
        f'lecture: "{lecture_label}"',
        f'date: "{current_date}"',
        'type: "Personal Scratchpad Notes"',
        "tags:",
        "  - scratchpad",
        "  - lecture-notes",
        "---",
        "",
        f"# {note_title}",
        "",
        f"> **Course**: {course_name}  ",
        f"> **Slide Deck**: `{pdf_name}` ({num_slides} Slides)  ",
        f"> **Date**: {current_date}  ",
        "",
        "---",
        "",
    ]

    for item in slide_items:
        i = item["index"]
        title = item["title"]
        rel_img = item["img_path"]

        lines.append(f"#### Slide {i:02d}: {title}")
        lines.append(f"![[{rel_img}]]")
        lines.append("")
        lines.append("### Spoken Lecture Takeaways & Audio Insights")
        lines.append("- ")
        lines.append("")
        lines.append("### Questions & Clarifications")
        lines.append("- ")
        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)


def render_slides(pdf_path, images_dir, dpi=150, pdftoppm_bin=None):
    """Render PDF slides to PNG images at specified DPI."""
    if not pdftoppm_bin:
        pdftoppm_bin = find_binary("pdftoppm")
    if not pdftoppm_bin:
        raise FileNotFoundError("pdftoppm binary not found. Please install poppler utilities.")

    images_dir = Path(images_dir).resolve()
    images_dir.mkdir(parents=True, exist_ok=True)

    ppm_prefix = images_dir / "slide"
    cmd = [pdftoppm_bin, "-png", "-r", str(dpi), str(pdf_path), str(ppm_prefix)]
    subprocess.run(cmd, check=True)

    rendered_images = sorted(list(images_dir.glob("slide-*.png")), key=natural_sort_key)
    for img in rendered_images:
        os.chmod(img, 0o644)

    return rendered_images


def generate_scratchpad(
    pdf_path,
    output_path,
    images_dir=None,
    dpi=150,
    title=None,
    course=None,
    lecture=None,
    force=False,
):
    """Programmatic entry point for generating lecture scratchpad notes."""
    pdf_p = Path(pdf_path).resolve()
    if not pdf_p.is_file():
        raise FileNotFoundError(f"Slide PDF not found at '{pdf_p}'")

    out_p = Path(output_path).resolve()
    if out_p.exists() and not force:
        raise FileExistsError(f"Output file already exists at '{out_p}'. Use force=True to overwrite.")

    # Determine images directory
    if images_dir:
        img_dir = Path(images_dir).resolve()
    else:
        pdf_parent = pdf_p.parent
        img_dir = pdf_parent / "images"

    # Render slides
    print(f"Rendering slides from '{pdf_p.name}' at {dpi} DPI to '{img_dir}'...")
    rendered_images = render_slides(pdf_p, img_dir, dpi=dpi)
    num_slides = len(rendered_images)
    if num_slides == 0:
        raise RuntimeError("No slide images were rendered.")

    # Extract slide texts
    slide_texts = extract_slide_texts(pdf_p)

    # Infer metadata
    meta = infer_metadata(pdf_p, out_p, course=course, lecture=lecture, title=title)

    # Prepare slide items
    slide_items = []
    for i, img_file in enumerate(rendered_images, start=1):
        rel_img = get_vault_relative_path(img_file, out_p)
        page_text = slide_texts[i - 1] if i - 1 < len(slide_texts) else ""
        slide_title = clean_slide_title(page_text, i)
        slide_items.append({
            "index": i,
            "title": slide_title,
            "img_path": rel_img,
        })

    # Build Markdown
    md_content = build_scratchpad_markdown(
        course_name=meta["course"],
        lecture_label=meta["lecture"],
        note_title=meta["title"],
        pdf_name=pdf_p.name,
        num_slides=num_slides,
        slide_items=slide_items,
    )

    out_p.parent.mkdir(parents=True, exist_ok=True)
    with open(out_p, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"Scratchpad successfully generated at: {out_p}")
    return out_p


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

    try:
        generate_scratchpad(
            pdf_path=args.pdf,
            output_path=args.output,
            images_dir=args.images_dir,
            dpi=args.dpi,
            title=args.title,
            course=args.course,
            lecture=args.lecture,
            force=args.force,
        )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
