# GLM-OCR — Setup

Follow the official repository: **https://github.com/zai-org/GLM-OCR**

It covers installation, model download, backend choice (local PyTorch / transformers, vLLM, hosted API, or any other supported deployment), and configuration. Use whichever backend the repo recommends for the target environment; this skill does not impose one.

After setup, verify:

```bash
python -c "from glmocr import GlmOcr; print('ok')"
```

If a custom `config.yaml` is needed for the chosen backend, place it in the working directory and pass it as `GlmOcr(config="config.yaml")`.
