#!/usr/bin/env python3
"""
Unit and Integration tests for Lecture Slide Scratchpad Generator (TDD Suite)
"""

import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

# Add scripts directory to sys.path
SCRIPT_DIR = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from generate_scratchpad import (
    find_binary,
    extract_slide_texts,
    clean_slide_title,
    get_vault_relative_path,
    infer_metadata,
    build_scratchpad_markdown,
    render_slides,
    generate_scratchpad,
)

MINIMAL_PDF_BYTES = b"""%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Count 2/Kids[3 0 R 4 0 R]>>endobj
3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<<>>>>endobj
4 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<<>>>>endobj
xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000052 00000 n 
0000000109 00000 n 
0000000186 00000 n 
trailer<</Size 5/Root 1 0 R>>
startxref
263
%%EOF
"""


class TestFindBinary(unittest.TestCase):
    def test_find_existing_system_binary(self):
        bin_path = find_binary("sh")
        self.assertIsNotNone(bin_path)
        self.assertTrue(os.path.isabs(bin_path))
        self.assertTrue(os.path.isfile(bin_path))

    def test_find_non_existent_binary(self):
        bin_path = find_binary("non_existent_binary_12345xyz")
        self.assertIsNone(bin_path)


class TestCleanSlideTitle(unittest.TestCase):
    def test_clean_standard_title(self):
        text = "Module 3: Cluster Analysis\nIntroduction to k-means\nPage 1"
        title = clean_slide_title(text, 1)
        self.assertEqual(title, "Module 3: Cluster Analysis")

    def test_clean_noise_and_numbers(self):
        text = "12\n08/09/2026\n• - *\nHierarchical Clustering Methods\nDetails below"
        title = clean_slide_title(text, 2)
        self.assertEqual(title, "Hierarchical Clustering Methods")

    def test_empty_text_fallback(self):
        title = clean_slide_title("", 5)
        self.assertEqual(title, "Slide 05")
        title_whitespace = clean_slide_title("   \n\n   \t ", 12)
        self.assertEqual(title_whitespace, "Slide 12")

    def test_short_title_combination(self):
        text = "K-Means\nAlgorithm Steps\nThird line"
        title = clean_slide_title(text, 3)
        self.assertEqual(title, "K-Means - Algorithm Steps")

    def test_long_title_truncation(self):
        text = "This is an extremely long lecture slide title that extends well beyond the standard character limit for headings and should be gracefully truncated with ellipses"
        title = clean_slide_title(text, 4)
        self.assertTrue(len(title) <= 70)
        self.assertTrue(title.endswith("..."))

    def test_strip_leading_bullets_and_numbers(self):
        text = "1.2) - Overview of Distance Metrics\nEuclidean vs Manhattan"
        title = clean_slide_title(text, 7)
        self.assertEqual(title, "Overview of Distance Metrics")


class TestVaultRelativePath(unittest.TestCase):
    def test_vault_marker_second_brain(self):
        target = "/Users/luca/Documents/Second-Brain/learning/tilburg-university/Data Mining/images/slide-01.png"
        note = "/Users/luca/Documents/Second-Brain/learning/tilburg-university/Data Mining/Week 3 - Personal Notes.md"
        rel = get_vault_relative_path(target, note)
        self.assertEqual(rel, "learning/tilburg-university/Data Mining/images/slide-01.png")

    def test_non_vault_path_relative_to_note_parent(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            note = Path(tmpdir) / "notes" / "note.md"
            img = Path(tmpdir) / "notes" / "images" / "slide-01.png"
            rel = get_vault_relative_path(img, note)
            self.assertEqual(rel, "images/slide-01.png")


class TestInferMetadata(unittest.TestCase):
    def test_infer_tilburg_course_and_week(self):
        pdf = Path("/Users/luca/Documents/Second-Brain/learning/tilburg-university/Data Mining/Materials/Modules/Module 3/slides.pdf")
        note = Path("/Users/luca/Documents/Second-Brain/learning/tilburg-university/Data Mining/Week 3 - Personal Notes.md")
        meta = infer_metadata(pdf, note)
        self.assertEqual(meta["course"], "Data Mining")
        self.assertEqual(meta["lecture"], "Week 3")
        self.assertEqual(meta["title"], "Week 3 — Personal Notes")

    def test_infer_explicit_overrides(self):
        pdf = Path("/path/to/slides.pdf")
        note = Path("/path/to/notes.md")
        meta = infer_metadata(
            pdf,
            note,
            course="Advanced AI",
            lecture="Lecture 5",
            title="Custom Lecture Title"
        )
        self.assertEqual(meta["course"], "Advanced AI")
        self.assertEqual(meta["lecture"], "Lecture 5")
        self.assertEqual(meta["title"], "Custom Lecture Title")


class TestBuildScratchpadMarkdown(unittest.TestCase):
    def test_build_markdown_structure(self):
        slide_items = [
            {"index": 1, "title": "Introduction to Clustering", "img_path": "images/slide-01.png"},
            {"index": 2, "title": "K-Means Objective Function", "img_path": "images/slide-02.png"},
        ]
        md = build_scratchpad_markdown(
            course_name="Data Mining",
            lecture_label="Week 3",
            note_title="Week 3 — Personal Notes",
            pdf_name="Lecture3-Clustering.pdf",
            num_slides=2,
            slide_items=slide_items,
            date_str="2026-09-08"
        )

        # 1. Check YAML Frontmatter
        self.assertTrue(md.startswith("---"))
        self.assertIn('course: "Data Mining"', md)
        self.assertIn('lecture: "Week 3"', md)
        self.assertIn('date: "2026-09-08"', md)
        self.assertIn('type: "Personal Scratchpad Notes"', md)
        self.assertIn('  - scratchpad', md)
        self.assertIn('  - lecture-notes', md)

        # 2. Check Document Header
        self.assertIn("# Week 3 — Personal Notes", md)
        self.assertIn("> **Course**: Data Mining", md)
        self.assertIn("> **Slide Deck**: `Lecture3-Clustering.pdf` (2 Slides)", md)
        self.assertIn("> **Date**: 2026-09-08", md)

        # 3. Check Slide 1 Structure
        self.assertIn("#### Slide 01: Introduction to Clustering", md)
        self.assertIn("![[images/slide-01.png]]", md)
        self.assertIn("### Spoken Lecture Takeaways & Audio Insights", md)
        self.assertIn("### Questions & Clarifications", md)

        # 4. Check Slide 2 Structure
        self.assertIn("#### Slide 02: K-Means Objective Function", md)
        self.assertIn("![[images/slide-02.png]]", md)

        # 5. Verify Clean Prompts Only (no pre-populated content)
        self.assertEqual(md.count("### Spoken Lecture Takeaways & Audio Insights\n- \n"), 2)
        self.assertEqual(md.count("### Questions & Clarifications\n- \n"), 2)


class TestScratchpadEndToEnd(unittest.TestCase):
    def test_end_to_end_generation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            pdf_path = tmppath / "slides.pdf"
            pdf_path.write_bytes(MINIMAL_PDF_BYTES)
            output_note = tmppath / "learning" / "tilburg-university" / "Machine Learning" / "Week 1 - Personal Notes.md"

            out = generate_scratchpad(
                pdf_path=pdf_path,
                output_path=output_note,
                dpi=72,
            )

            self.assertTrue(output_note.exists())
            self.assertEqual(out, output_note.resolve())

            content = output_note.read_text(encoding="utf-8")
            self.assertIn('course: "Machine Learning"', content)
            self.assertIn('lecture: "Week 1"', content)
            self.assertIn("#### Slide 01: Slide 01", content)
            self.assertIn("#### Slide 02: Slide 02", content)
            self.assertIn("### Spoken Lecture Takeaways & Audio Insights", content)

            # Check rendered images
            images_dir = tmppath / "images"
            self.assertTrue(images_dir.exists())
            images = list(images_dir.glob("slide-*.png"))
            self.assertEqual(len(images), 2)

    def test_force_overwrite_protection(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            pdf_path = tmppath / "slides.pdf"
            pdf_path.write_bytes(MINIMAL_PDF_BYTES)
            output_note = tmppath / "note.md"
            output_note.write_text("Existing Content")

            # Without force, should raise FileExistsError
            with self.assertRaises(FileExistsError):
                generate_scratchpad(pdf_path=pdf_path, output_path=output_note, force=False)

            # With force, should succeed
            generate_scratchpad(pdf_path=pdf_path, output_path=output_note, force=True, dpi=72)
            self.assertIn("# Lecture — Personal Notes", output_note.read_text())


class TestScratchpadCLI(unittest.TestCase):
    def test_cli_missing_args(self):
        script_path = SCRIPT_DIR / "generate_scratchpad.py"
        cmd = [sys.executable, str(script_path)]
        res = subprocess.run(cmd, capture_output=True, text=True)
        self.assertNotEqual(res.returncode, 0)
        self.assertIn("usage:", res.stderr.lower())

    def test_cli_execution_success(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            pdf_path = tmppath / "slides.pdf"
            pdf_path.write_bytes(MINIMAL_PDF_BYTES)
            output_note = tmppath / "Week 2 - Personal Notes.md"

            script_path = SCRIPT_DIR / "generate_scratchpad.py"
            cmd = [
                sys.executable,
                str(script_path),
                "--pdf", str(pdf_path),
                "--output", str(output_note),
                "--dpi", "72",
                "--course", "Data Science",
                "--lecture", "Week 2",
            ]
            res = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(res.returncode, 0, f"CLI error: {res.stderr}")
            self.assertTrue(output_note.exists())
            self.assertIn('course: "Data Science"', output_note.read_text())


if __name__ == "__main__":
    unittest.main()
