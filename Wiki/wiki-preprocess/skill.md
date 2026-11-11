---
name: wiki-preprocess
description: >
  Preprocessa file multimediali e documenti prima dell'ingest nel wiki.
  Usa questa skill quando ci sono file audio, immagini, documenti Office
  (docx, pptx, xlsx) o altri formati non leggibili come testo nelle cartelle
  raw/ o in altre inbox del vault, che devono essere convertiti o descritti
  prima che wiki-ingest possa leggerli.
---

# Wiki Preprocess

Converte e prepara file multimediali per l'ingest automatico nel wiki.

---

## Contratto comune

Questa skill deve servire vault diversi.

Non assumere che l'audio viva sempre nelle stesse cartelle.

Il file istruzioni locale del vault può dichiarare:

- cartelle audio
- cartelle transcript
- inbox aggiuntive
- tool o script preferiti per il preprocessing

Usa quei path come fonte di verità. In assenza di override, cerca i file audio nelle aree `raw/` e nelle altre inbox esistenti del vault.

---

## Audio

Tool disponibile: lo script `scripts/preprocess-audio.py` incluso in questa skill. Cercalo nella directory di installazione della skill. Se non è raggiungibile, usa whisper o tool equivalente disponibile nell'ambiente.

Formati tipici:

- `.m4a`
- `.opus`
- `.wav`
- `.ogg`
- `.flac`
- `.aac`
- `.wma`
- `.mp3`

Flusso:

1. converte in formato utile per speech
2. trascrive con whisper o tool equivalente
3. salva `<nome-audio>.transcription.md` accanto al file originale — questo è il nome canonico che `wiki-ingest` si aspetta

Se il file `.transcription.md` esiste già e ha `updated:` più recente dell'audio, salta.

Uso:

```bash
python <path-skill>/scripts/preprocess-audio.py
python <path-skill>/scripts/preprocess-audio.py <cartella>
python <path-skill>/scripts/preprocess-audio.py --dry-run
```

---

## Link e URL

Quando l'input è un link o un URL da ingestare, attiva la skill `crawl4ai`.

Flusso operativo:

1. Riconosci i link in ingresso come risorsa web anziché file locale
2. Attiva `crawl4ai` per il crawling e l'estrazione del contenuto
3. Usa il contenuto estratto come base per la conversione o l'ingest successivo

---

## Office e documenti strutturati

Per i documenti Office e i formati strutturati (Word, PowerPoint, Excel e affini) usa **markitdown**, che li converte in Markdown preservando titoli, tabelle, liste e struttura.

Tool disponibile: lo script `scripts/preprocess-office.py` incluso in questa skill. **Non riscrivere la conversione da zero**: usa lo script. Cercalo nella directory di installazione della skill.

Formati gestiti:

- `.docx`, `.doc` (Word)
- `.pptx`, `.ppt` (PowerPoint)
- `.xlsx`, `.xls` (Excel)
- `.odt`, `.odp`, `.ods` (OpenDocument)
- `.rtf`, `.epub`
- `.csv`, `.tsv`, `.html`, `.htm`, `.xml`, `.json`, `.ipynb`

Flusso:

1. lo script scansiona i file/cartelle passati (default `raw/`)
2. converte ogni documento con markitdown
3. salva il risultato come `<nome-file-completo>.md` accanto all'originale (es. `Report Q3.docx` → `Report Q3.docx.md`) — questo è il nome canonico che `wiki-ingest` si aspetta

È idempotente: se il `.md` esiste ed è più recente del documento, salta.

Uso:

```bash
python <path-skill>/scripts/preprocess-office.py                 # scansiona ./raw
python <path-skill>/scripts/preprocess-office.py raw inbox       # più cartelle
python <path-skill>/scripts/preprocess-office.py report.docx     # singolo file
python <path-skill>/scripts/preprocess-office.py --dry-run        # anteprima
```

Prerequisito: `pip install 'markitdown[all]'`.

I formati binari legacy (`.doc`, `.ppt`, `.xls`) a volte non sono leggibili direttamente da markitdown: in quel caso convertili prima con LibreOffice (`libreoffice --headless --convert-to docx <file>`) e poi rilancia lo script. Lo script segnala questi casi.

---

## Immagini e PDF scansionati

Per immagini e PDF scansionati (non-native-text), attiva la skill `glm-ocr` e delega a essa l'estrazione del testo.

- Non riassumere in questa skill il comportamento interno di `glm-ocr`.
- Usa `glm-ocr` come skill specializzata per trasformare l'immagine o il PDF scansionato in Markdown.
- Salva il risultato accanto al file originale come `<nome-file>.ocr.md` — questo è il nome canonico che `wiki-ingest` si aspetta.
- Fornisci il `.ocr.md` prodotto come source a `wiki-ingest`.

Se `glm-ocr` non è configurato o Ollama non è disponibile:

- se il modello corrente supporta vision: descrivi direttamente il contenuto dell'immagine
- altrimenti: chiedi all'utente una descrizione testuale

**PDF native-text** (non scansionati): leggi direttamente senza OCR — `glm-ocr` aggiunge overhead inutile.

---

## Relazione con wiki-ingest

`wiki-ingest` non esegue conversioni.

Quando trova un file audio:

1. cerca `.transcription.md`
2. se esiste, usa quello
3. se non esiste, richiede `wiki-preprocess`

Quando trova un'immagine o un PDF scansionato:

1. cerca `.ocr.md` accanto al file
2. se esiste, usa quello
3. se non esiste, usa `glm-ocr` via `wiki-preprocess` per generarlo

Quando trova un documento Office o strutturato (docx, pptx, xlsx, …):

1. cerca `<nome-file-completo>.md` accanto al file
2. se esiste, usa quello
3. se non esiste, lancia `scripts/preprocess-office.py` via `wiki-preprocess` per generarlo
