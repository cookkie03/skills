---
name: wiki-preprocess
description: >
  Preprocessa file multimediali prima dell'ingest nel wiki.
  Usa questa skill quando ci sono file audio, immagini o altri formati non testuali
  nelle cartelle raw/ o in altre inbox del vault che devono essere convertiti o
  descritti prima che wiki-ingest possa leggerli.
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

Tool preferito di default:

- `Second-Brain/scripts/preprocess-audio.py`

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
3. salva `.transcription.md` accanto al file originale

Se `.transcription.md` esiste già ed è più recente dell'audio, salta.

Uso:

```bash
python .agents/skills/wiki-preprocess/scripts/preprocess-audio.py
python .agents/skills/wiki-preprocess/scripts/preprocess-audio.py <cartella>
python .agents/skills/wiki-preprocess/scripts/preprocess-audio.py --dry-run
```

---

## Link e URL

Quando l'input è un link o un URL da ingestare, attiva la skill `crawl4ai`.

Flusso operativo:

1. Riconosci i link in ingresso come risorsa web anziché file locale
2. Attiva `crawl4ai` per il crawling e l'estrazione del contenuto
3. Usa il contenuto estratto come base per la conversione o l'ingest successivo

---

## Immagini e PDF scansionati

Per immagini e PDF scansionati (non-native-text), attiva la skill `glm-ocr` e delega a essa l'estrazione del testo.

- Non riassumere in questa skill il comportamento interno di `glm-ocr`.
- Usa `glm-ocr` come skill specializzata per trasformare l'immagine o il PDF scansionato in Markdown.
- Salva il risultato in una cartella dedicata (es. `raw/ocr-output/`) o accanto al file originale come `.ocr.md`.
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
