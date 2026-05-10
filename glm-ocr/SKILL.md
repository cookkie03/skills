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

Extracts text, tables, and formulas from images/PDFs via a local Ollama server. Output: clean Markdown + structured JSON.

## Prerequisito

Ollama deve girare localmente con il modello scaricato. Se non è configurato, vedi `SETUP.md`.

Verifica rapida:
```bash
ollama list  # deve mostrare glm-ocr:latest
```

## Usage

Il `config.yaml` nella directory della skill configura il backend Ollama. Passane il path a `GlmOcr`:

```python
from glmocr import GlmOcr

config = "/path/to/skills/glm-ocr/config.yaml"  # adatta al path reale

with GlmOcr(config_path=config) as ocr:
    result = ocr.parse("file.pdf")   # accetta .png .jpg .jpeg .webp .pdf
    result.save("./output")          # scrive result.md + result.json
    print(result.markdown_result)    # oppure leggi direttamente
```

Per più file:
```python
with GlmOcr(config_path=config) as ocr:
    result = ocr.parse(["page1.png", "page2.png"])
    result.save("./output")
```

## Output

- `result.md` — Markdown (tabelle GFM, formule come `$...$` / `$$...$$`)
- `result.json` — risultato strutturato con bounding box per blocco
- `result.markdown_result` — stringa Markdown accessibile direttamente in Python

> Nota: i risultati OCR devono essere salvati con lo stesso nome e lo stesso percorso dei file di origine, per mantenere la corrispondenza tra input e output.

## Troubleshooting

**502 Bad Gateway**: assicurati che `config.yaml` abbia `api_path: /api/generate` e `api_mode: ollama_generate`.

**Modello non trovato**: esegui `ollama pull glm-ocr:latest`.

**Ollama non risponde**: esegui `ollama serve`.
