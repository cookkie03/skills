# GLM-OCR via Ollama — Usage Skill

## What this skill is for
Use this skill whenever the user wants to run OCR on images or PDF documents using the **GLM-OCR model** served locally via **Ollama**.

GLM-OCR is a state-of-the-art open-source OCR model (0.9B params, MIT license) that extracts text, tables, and formulas from documents, outputting clean Markdown.

---

## Prerequisites check
Before proceeding, **always verify** that the setup is in place:

```bash
# 1. Is Ollama running?
ollama ps

# 2. Is the model available?
ollama list | grep glm-ocr

# 3. Quick connectivity test
curl -s http://localhost:11434/api/generate \
  -d '{"model":"glm-ocr:latest","prompt":"Hello","stream":false}' \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print('OK' if d.get('response') else 'FAIL')"
```

If any of these fail → see **Troubleshooting** below.

---

## Usage

### Via glmocr SDK (recommended)

**Single image:**
```bash
glmocr --images path/to/image.png --output-dir ./output
```

**PDF document:**
```bash
glmocr --images path/to/document.pdf --output-dir ./output
```

**Multiple pages (as separate images):**
```bash
glmocr --images page1.png page2.png page3.png --output-dir ./output
```

Output files written to `./output/`:
- `result.md` — extracted content in Markdown
- `result.json` — structured result with bounding boxes

---

### Via Python API

```python
from glmocr import GlmOcr

ocr = GlmOcr(config="config.yaml")
result = ocr.parse(images=["path/to/image.png"])
print(result.markdown)
result.save("./output")
```

---

### Via raw curl (no SDK, direct Ollama)

```bash
# Encode image to base64 and call Ollama directly
BASE64=$(base64 -i path/to/image.png)

curl http://localhost:11434/api/generate \
  -d "{
    \"model\": \"glm-ocr:latest\",
    \"prompt\": \"<image>\",
    \"images\": [\"$BASE64\"],
    \"stream\": false
  }"
```

---

## config.yaml (required for SDK usage)

Place this file in your working directory:

```yaml
pipeline:
  maas:
    enabled: false
  ocr_api:
    api_host: localhost
    api_port: 11434
    api_path: /api/generate     # Ollama native endpoint
    model: glm-ocr:latest
    api_mode: ollama_generate   # Required: enables Ollama format conversion
```

> **Note:** Do NOT use the OpenAI-compatible endpoint (`/v1/chat/completions`) — Ollama's vision support there is limited. Always use `/api/generate` with `api_mode: ollama_generate`.

---

## Output format

GLM-OCR returns Markdown. Examples:
- Plain text → returned as-is (no extra formatting)
- Tables → Markdown table syntax
- Formulas → LaTeX inside `$...$` or `$$...$$`
- Mixed documents → structured Markdown with headings

---

## Tips

- **First request is slow** — Ollama loads the model into memory. Subsequent requests are much faster.
- **Large images / PDFs** — increase context window if output is truncated (see Troubleshooting).
- **Batch processing** — for multiple independent documents, call the endpoint once per document.

---

## Troubleshooting

| Symptom | Likely cause | Action |
|---|---|---|
| `ollama: command not found` | Ollama not installed | → See `SETUP.md` |
| `glm-ocr:latest` not in `ollama list` | Model not pulled | → See `SETUP.md` |
| Ollama not running (`connection refused`) | Service not started | `ollama serve` |
| Gibberish / empty output | Context window too small | → See `SETUP.md` § Custom Modelfile |
| `GGML_ASSERT` crash | Known Ollama bug with some versions | → See `SETUP.md` § Known Issues |
| `api_mode` error in SDK | Wrong config | Check `config.yaml` has `api_mode: ollama_generate` |
| SDK sends OpenAI format to Ollama | Missing `api_mode` key | Add `api_mode: ollama_generate` to config |

> **If Ollama or the model are missing**, load `SETUP.md` (in the same folder as this file) for complete installation instructions.

---

## Reference
- GitHub: https://github.com/zai-org/GLM-OCR
- Ollama deploy guide: https://github.com/zai-org/GLM-OCR/blob/main/examples/ollama-deploy/README.md
- DeepWiki (architecture): https://deepwiki.com/zai-org/GLM-OCR/3.5-ollama-deployment
