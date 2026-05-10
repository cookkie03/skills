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

## Immagini

Per ora il preprocessing delle immagini è spesso manuale.

Se il modello supporta vision:

- descrivi direttamente il contenuto

Altrimenti:

- chiedi all'utente una descrizione testuale da poter utilizzare per continuare

---

## Relazione con wiki-ingest

`wiki-ingest` non esegue conversioni.

Quando trova un file audio:

1. cerca `.transcription.md`
2. se esiste, usa quello
3. se non esiste, richiede `wiki-preprocess`
