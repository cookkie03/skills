# GLM-OCR — Setup (Ollama)

## 1. Installa Ollama

```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

## 2. Scarica il modello

```bash
ollama pull glm-ocr:latest
```

## 3. Avvia il server

```bash
ollama serve
```

Gira su `http://localhost:11434`. Di solito parte automaticamente dopo l'installazione.

## 4. Verifica

```bash
python -c "from glmocr import GlmOcr; print('ok')"
ollama list  # glm-ocr:latest deve comparire
```

---

Il `config.yaml` nella stessa cartella di questa skill è già configurato per Ollama. Copialo nella working directory prima di usare la skill, oppure passane il path direttamente a `GlmOcr(config_path=...)`.
