# GLM-OCR — Setup (Ollama + PP-DocLayoutV3)

## 1. Installa Ollama

```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

## 2. Scarica il modello GLM-OCR

```bash
ollama pull glm-ocr:latest
```

## 3. Avvia il server Ollama

```bash
ollama serve
```

Gira su `http://localhost:11434`. Di solito parte automaticamente dopo l'installazione su macOS.

## 4. Installa la dipendenza Python

```bash
pip install 'glmocr[layout]'
```

L'extra `[layout]` installa anche il supporto per PP-DocLayoutV3 (modulo `transformers` con `PPDocLayoutV3ForObjectDetection`). Senza di esso si ottiene `ImportError: PPDocLayoutV3ForObjectDetection`.

## 5. Pre-scarica PP-DocLayoutV3 (consigliato)

Il `config.yaml` della skill punta a `PaddlePaddle/PP-DocLayoutV3_safetensors`, che verrà scaricato automaticamente da Hugging Face al primo uso (~2 GB). Per evitare di pagare quel costo al primo OCR, pre-popolalo:

```bash
python -c "
from huggingface_hub import snapshot_download
snapshot_download('PaddlePaddle/PP-DocLayoutV3_safetensors')
"
```

Il modello viene messo nella cache HF condivisa (`~/.cache/huggingface/hub/`), quindi non serve gestire path locali.

## 6. Verifica

```bash
ollama list                                      # glm-ocr:latest deve comparire
python -c "from glmocr import GlmOcr; print('ok')"
```

---

## Deployment: sempre Ollama in locale

Tutta la pipeline OCR (sia inference GLM-OCR sia layout detection PP-DocLayoutV3) gira in locale:

- **GLM-OCR** → servito da Ollama su `http://localhost:11434` (deployment `ollama_generate`)
- **PP-DocLayoutV3** → caricato in-process via `transformers`, pesi da cache HF locale

Nessuna chiamata a servizi remoti, nessuna API key richiesta. Il `config.yaml` ha `pipeline.maas.enabled: false` proprio per garantire questo.
