#!/usr/bin/env python3
"""
extract_slides.py - Extract slide-by-slide text and render high-resolution slide PNG images.
Multi-backend support:
- macOS native Swift / PDFKit (zero dependencies)
- pdftoppm (poppler)
- PyMuPDF (fitz)
- pypdf for text fallback
"""

import os
import sys
import shutil
import tempfile
import argparse
import subprocess
from typing import Optional

try:
    import pypdf
except ImportError:
    pypdf = None


SWIFT_RENDER_SCRIPT = """
import Foundation
import PDFKit
import AppKit

let args = CommandLine.arguments
guard args.count >= 3 else {
    print("Usage: swift render.swift <pdf_path> <output_dir> [dpi] [prefix]")
    exit(1)
}

let pdfPath = args[1]
let outputDir = args[2]
let dpi: CGFloat = args.count > 3 ? CGFloat(Double(args[3]) ?? 150.0) : 150.0
let prefix = args.count > 4 ? args[4] : "slide"
let scale = dpi / 72.0

guard let pdfDoc = PDFDocument(url: URL(fileURLWithPath: pdfPath)) else {
    print("Error: Could not open PDF at \(pdfPath)")
    exit(1)
}

try? FileManager.default.createDirectory(atPath: outputDir, withIntermediateDirectories: true)

let pageCount = pdfDoc.pageCount
let numDigits = max(2, String(pageCount).count)

for i in 0..<pageCount {
    guard let page = pdfDoc.page(at: i) else { continue }
    let pageRect = page.bounds(for: .mediaBox)
    let pixelSize = NSSize(width: pageRect.width * scale, height: pageRect.height * scale)
    
    let image = NSImage(size: pixelSize)
    image.lockFocus()
    
    guard let context = NSGraphicsContext.current?.cgContext else {
        image.unlockFocus()
        continue
    }
    
    context.setFillColor(NSColor.white.cgColor)
    context.fill(CGRect(origin: .zero, size: pixelSize))
    
    context.scaleBy(x: scale, y: scale)
    page.draw(with: .mediaBox, to: context)
    
    image.unlockFocus()
    
    guard let tiffData = image.tiffRepresentation,
          let bitmap = NSBitmapImageRep(data: tiffData),
          let pngData = bitmap.representation(using: .png, properties: [:]) else {
        continue
    }
    
    let pageNumberStr = String(format: "%0\(numDigits)d", i + 1)
    let outPath = "\(outputDir)/\(prefix)-\(pageNumberStr).png"
    try? pngData.write(to: URL(fileURLWithPath: outPath))
}
print("Rendered \(pageCount) slide images to \(outputDir)")
"""


def render_images_swift(pdf_path: str, output_dir: str, dpi: int = 150, prefix: str = "slide") -> bool:
    if not shutil.which("swift"):
        return False
    with tempfile.NamedTemporaryFile(suffix=".swift", mode="w", encoding="utf-8") as tf:
        tf.write(SWIFT_RENDER_SCRIPT)
        tf.flush()
        cmd = ["swift", tf.name, pdf_path, output_dir, str(dpi), prefix]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode == 0:
            print(f"  [Images] {res.stdout.strip()}")
            return True
        else:
            print(f"  [Images Swift Error]: {res.stderr.strip()}", file=sys.stderr)
            return False


def render_images_pdftoppm(pdf_path: str, output_dir: str, dpi: int = 150, prefix: str = "slide") -> bool:
    if not shutil.which("pdftoppm"):
        return False
    os.makedirs(output_dir, exist_ok=True)
    out_prefix = os.path.join(output_dir, prefix)
    cmd = ["pdftoppm", "-png", "-r", str(dpi), pdf_path, out_prefix]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode == 0:
        print(f"  [Images] Rendered slide images via pdftoppm to '{output_dir}'")
        return True
    return False


def render_images_fitz(pdf_path: str, output_dir: str, dpi: int = 150, prefix: str = "slide") -> bool:
    try:
        import fitz
    except ImportError:
        return False
    os.makedirs(output_dir, exist_ok=True)
    doc = fitz.open(pdf_path)
    zoom = dpi / 72.0
    mat = fitz.Matrix(zoom, zoom)
    num_digits = max(2, len(str(len(doc))))
    for idx, page in enumerate(doc):
        pix = page.get_pixmap(matrix=mat)
        page_num_str = f"{idx + 1:0{num_digits}d}"
        pix.save(os.path.join(output_dir, f"{prefix}-{page_num_str}.png"))
    print(f"  [Images] Rendered {len(doc)} slide images via PyMuPDF to '{output_dir}'")
    return True


def render_slide_images(pdf_path: str, output_dir: str, dpi: int = 150, prefix: str = "slide") -> bool:
    os.makedirs(output_dir, exist_ok=True)
    if sys.platform == "darwin" and render_images_swift(pdf_path, output_dir, dpi, prefix):
        return True
    if render_images_pdftoppm(pdf_path, output_dir, dpi, prefix):
        return True
    if render_images_fitz(pdf_path, output_dir, dpi, prefix):
        return True
    print("  [Warning] No suitable image renderer found (swift, pdftoppm, or fitz). Skipping image rendering.", file=sys.stderr)
    return False


def extract_pdf(pdf_path: str, output_path: Optional[str] = None, images_dir: Optional[str] = None, render_imgs: bool = True, dpi: int = 150) -> str:
    if not os.path.isfile(pdf_path):
        raise FileNotFoundError(f"File not found: {pdf_path}")

    pdf_dir = os.path.dirname(os.path.abspath(pdf_path))
    deck_name = os.path.basename(pdf_path)
    base_name, _ = os.path.splitext(deck_name)

    if output_path is None:
        output_path = os.path.join(pdf_dir, f"{base_name}_extract.md")

    if images_dir is None:
        # If output_path is inside a staging folder, default images to staging images
        if ".staging_unified" in output_path:
            staging_root = output_path.split(".staging_unified")[0] + ".staging_unified"
            images_dir = os.path.join(staging_root, "images")
        else:
            images_dir = os.path.join(pdf_dir, "images")

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    os.makedirs(os.path.abspath(images_dir), exist_ok=True)

    # 1. Render Images
    if render_imgs:
        print(f"\nRendering slide images for '{deck_name}' to '{images_dir}'...")
        render_slide_images(pdf_path, images_dir, dpi=dpi, prefix="slide")

    # 2. Extract Text
    print(f"Extracting slide text from '{deck_name}'...")
    lines = [f"# Slide Text Extract: {deck_name}\n"]

    extracted = False
    try:
        import fitz
        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        num_digits = max(2, len(str(total_pages)))
        for idx, page in enumerate(doc):
            text = page.get_text() or ""
            page_str = f"{idx + 1:0{num_digits}d}"
            lines.append(f"## Slide {idx + 1}\n![[slide-{page_str}.png]]\n\n{text.strip()}\n")
        extracted = True
    except ImportError:
        pass

    if not extracted and pypdf is not None:
        reader = pypdf.PdfReader(pdf_path)
        total_pages = len(reader.pages)
        num_digits = max(2, len(str(total_pages)))
        for idx, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            page_str = f"{idx + 1:0{num_digits}d}"
            lines.append(f"## Slide {idx + 1}\n![[slide-{page_str}.png]]\n\n{text.strip()}\n")
        extracted = True

    if not extracted:
        raise ImportError("pypdf or fitz (PyMuPDF) is required for text extraction. Install with: pip install pypdf")

    content = "\n".join(lines)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Extracted {total_pages} slides -> '{output_path}'")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Extract slide text and render images from PDF files to markdown.")
    parser.add_argument("target", help="Path to PDF file or directory containing PDF files.")
    parser.add_argument("-o", "--output", help="Optional explicit output markdown path.", default=None)
    parser.add_argument("--images-dir", help="Optional explicit images directory (default: .staging_unified/images/ or local images/).", default=None)
    parser.add_argument("--no-images", action="store_true", help="Disable rendering PNG slide images.")
    parser.add_argument("--dpi", type=int, default=150, help="Image resolution DPI (default: 150).")
    args = parser.parse_args()

    render_imgs = not args.no_images

    if os.path.isfile(args.target) and args.target.lower().endswith(".pdf"):
        extract_pdf(args.target, output_path=args.output, images_dir=args.images_dir, render_imgs=render_imgs, dpi=args.dpi)
    elif os.path.isdir(args.target):
        found = False
        for root, _, files in os.walk(args.target):
            for file in files:
                if file.lower().endswith(".pdf") and not file.startswith("."):
                    pdf_path = os.path.join(root, file)
                    extract_pdf(pdf_path, images_dir=args.images_dir, render_imgs=render_imgs, dpi=args.dpi)
                    found = True
        if not found:
            print(f"No PDF files found in {args.target}")
    else:
        print(f"Invalid target: {args.target}. Must be a PDF file or directory.")
        sys.exit(1)


if __name__ == "__main__":
    main()
