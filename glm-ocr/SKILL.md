---
name: glm-ocr
description: >
  Run OCR on images or PDF documents using GLM-OCR to extract text, tables,
  and formulas as clean Markdown. Use whenever the user wants to OCR a file,
  transcribe a scan, parse a handwritten note, or extract structured content
  from a document image.
  Triggers: "OCR this", "estrai testo", "leggi questo PDF scansionato",
  "trascrivi documento", "extract text from image", "parse this scan",
  "read handwritten notes".
---

# GLM-OCR

Extracts text, tables, and formulas from images/PDFs. Output: clean Markdown + structured JSON.

Reference: https://github.com/zai-org/GLM-OCR — follow that repo for any setup, configuration, or model-backend choice. This skill stays backend-agnostic and does not pin Ollama, vLLM, or transformers.

## Usage

```python
from glmocr import GlmOcr
ocr = GlmOcr()                            # or GlmOcr(config="config.yaml")
result = ocr.parse(images=["file.pdf"])   # accepts .png .jpg .jpeg .webp .pdf, single or list
result.save("./output")                   # writes result.md + result.json
```

Pass a `config.yaml` only if the chosen backend requires one (see the official repo).

## Output

- `result.md` — Markdown (tables in GFM, formulas as `$...$` / `$$...$$`)
- `result.json` — structured result with bounding boxes per block

## Setup

If `glmocr` is not installed or the model isn't available, see `SETUP.md` — it points to the official repo.

## When to use this skill

Use it for files on the local filesystem that need OCR: scanned PDFs, photographed pages, screenshots of dense documents, handwriting. For native text PDFs that can be read directly, prefer reading the file as text — OCR adds overhead without benefit.
