# GLM-OCR via Ollama — Setup & Installation

> **When to load this file:** Only when `SKILL.md` troubleshooting indicates missing installation (Ollama not found, model not pulled, or crash during inference).

---

## 1. Install Ollama

**macOS (Homebrew — recommended):**
```bash
brew install ollama
```

**macOS (manual):**
Download from https://ollama.com/download and run the `.dmg` installer.

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows:** Download installer from https://ollama.com/download/windows

---

## 2. Start the Ollama service

Ollama should auto-start on macOS after installation.  
If not (or on Linux):

```bash
ollama serve
```

Verify it's running:
```bash
curl http://localhost:11434/api/tags
# Should return JSON with "models" field
```

---

## 3. Pull the GLM-OCR model

```bash
ollama pull glm-ocr:latest
```

> First pull downloads ~1–2 GB of model weights. Wait for completion before proceeding.

Verify:
```bash
ollama list | grep glm-ocr
```

---

## 4. Install the glmocr SDK

The SDK handles layout detection, image splitting, parallel OCR, and Markdown formatting — it wraps the raw Ollama API.

```bash
pip install glmocr[layout]
```

> `[layout]` extra is required for self-hosted mode (enables PP-DocLayout-V3 for document layout analysis).

Verify:
```bash
glmocr --help
```

---

## 5. Create config.yaml

In your project folder:

```yaml
pipeline:
  maas:
    enabled: false
  ocr_api:
    api_host: localhost
    api_port: 11434
    api_path: /api/generate
    model: glm-ocr:latest
    api_mode: ollama_generate
```

---

## Custom Modelfile (fix for gibberish/truncated output)

If you get incomplete or garbled output, the default context window is too small. Create a custom model with a larger context:

```bash
cat > Modelfile <<EOF
FROM glm-ocr:latest
PARAMETER num_ctx 10240
TEMPLATE {{ .Prompt }}
RENDERER glm-ocr
PARSER glm-ocr
PARAMETER temperature 0
EOF

ollama create glm-ocr-large -f Modelfile
```

Then update your `config.yaml`:
```yaml
model: glm-ocr-large
```

---

## Known Issues

### `GGML_ASSERT(a->ne[2] * 4 == b->ne[0]) failed` crash
**Cause:** Bug in some Ollama builds with the default context window.  
**Fix:** Use the custom Modelfile above with `num_ctx 10240`.

### OpenAI format error / wrong API mode
**Symptom:** Responses look like chat completions, not OCR output.  
**Fix:** Ensure `api_mode: ollama_generate` is set in `config.yaml`. Do NOT use `/v1/chat/completions`.

### Slow first request
**Cause:** Normal — Ollama loads model weights into RAM/VRAM on first call.  
**Fix:** No action needed. Keep Ollama running to avoid reload delays.

---

## Uninstall

```bash
# Remove model
ollama rm glm-ocr:latest

# macOS
rm /usr/local/bin/ollama
# Or use the app uninstaller if installed via .dmg

# Linux
sudo rm /usr/local/bin/ollama
```

---

## Reference
- Ollama: https://ollama.com
- GLM-OCR repo: https://github.com/zai-org/GLM-OCR
- Ollama deploy README: https://github.com/zai-org/GLM-OCR/blob/main/examples/ollama-deploy/README.md
- Known issues discussion: https://huggingface.co/zai-org/GLM-OCR/discussions/8
