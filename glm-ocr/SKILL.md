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

Estrae testo, tabelle e formule da immagini/PDF via Ollama in locale, con layout detection strutturato tramite PP-DocLayoutV3. Output: Markdown pulito + JSON con bounding box.

## Prerequisiti

Ollama deve girare con il modello scaricato, e PP-DocLayoutV3 deve essere disponibile (auto-download al primo uso). Se non è configurato, vedi `SETUP.md`.

```bash
ollama list  # deve mostrare glm-ocr:latest
```

Dipendenza Python richiesta:

```bash
pip install 'glmocr[layout]'
```

## Utilizzo

```python
import os
from glmocr import GlmOcr

SKILL_DIR = "/path/to/skills/glm-ocr"   # adatta al path reale
CONFIG_PATH = os.path.join(SKILL_DIR, "config.yaml")

with GlmOcr(config_path=CONFIG_PATH) as ocr:
    result = ocr.parse("documento.pdf")   # accetta .png .jpg .jpeg .webp .pdf
    result.save("./output")               # scrive result.md + result.json
    print(result.markdown_result)
```

Per più file:

```python
with GlmOcr(config_path=CONFIG_PATH) as ocr:
    result = ocr.parse(["page1.png", "page2.png"])
    result.save("./output")
```

Al primo run la pipeline scaricherà PP-DocLayoutV3 da Hugging Face (~2 GB, una sola volta) nella cache HF locale. I run successivi partono immediatamente.

## Parametri di qualità nel config.yaml

Il `config.yaml` della skill è già ottimizzato per qualità su deployment Ollama:

| Parametro | Valore | Effetto |
|-----------|--------|---------|
| `layout.model_dir` | `PaddlePaddle/PP-DocLayoutV3_safetensors` | Layout detector strutturato (colonne, tabelle, figure, formule) |
| `page_loader.dpi` | 300 | Risoluzione rendering PDF → immagini (più alto = migliore qualità, più lento) |
| `ocr_api.request_timeout` | 300 | Timeout per richiesta a Ollama (300 s per immagini grandi) |
| `page_loader.task_prompt_mapping` | testo/tabella/formula | Prompt che guidano GLM-OCR per ciascun tipo di blocco rilevato |

Per documenti con testo molto piccolo o scansioni di bassa qualità, alza a `dpi: 400` nel config.yaml. Per documenti puliti puoi ridurre a `dpi: 200` per velocizzare.

## Output

- `result.md` — Markdown (tabelle GFM, formule come `$...$` / `$$...$$`)
- `result.json` — risultato strutturato con bounding box per blocco
- `result.markdown_result` — stringa Markdown accessibile direttamente in Python

> Nota: i risultati OCR devono essere salvati con lo stesso nome e lo stesso percorso dei file di origine, per mantenere la corrispondenza tra input e output.

## Troubleshooting

**ImportError: PPDocLayoutV3ForObjectDetection** → `pip install 'glmocr[layout]'`

**ValueError: pipeline.layout.model_dir is required** → il `config.yaml` della skill lo include già (`PaddlePaddle/PP-DocLayoutV3_safetensors`). Verifica di stare passando il path corretto a `GlmOcr(config_path=...)`.

**Primo run molto lento / blocco a "downloading"** → normale: PP-DocLayoutV3 sta scaricando ~2 GB. Aspetta che la cache HF si popoli (`~/.cache/huggingface/hub/`). I run successivi sono immediati.

**Output vuoto (0 chars)** → il `task_prompt_mapping` manca dal config.yaml. Il `config.yaml` della skill lo include già; verifica di stare usando quello corretto.

**Timeout / risposta lenta** → normale per immagini grandi. Il timeout è a 300 s. Se scade ancora, riduci il DPI o processa meno pagine per volta.

**502 Bad Gateway** → verifica che `api_path: /api/generate` e `api_mode: ollama_generate` siano nel config.yaml (già configurati).

**Modello GLM non trovato** → `ollama pull glm-ocr:latest`

**Ollama non risponde** → `ollama serve`
