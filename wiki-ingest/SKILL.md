---
name: wiki-ingest
description: >
  Ingests new information into an LLM Wiki vault. Use this skill whenever the user wants
  to add new knowledge, process raw sources, or update existing wiki content.
  Triggers include: "ingest [file]", "processa questo", "aggiungi alla wiki",
  "aggiorna la lista", "ho letto X", "segna che ho finito Y", "rimuovi questa info",
  "sintetizza la sezione Z", "aggiorna il todo".
  This skill handles BOTH new knowledge ingestion AND updates/edits to existing wiki pages.
  Can operate autonomously by reading the raw/ folder without explicit user instructions.
---

# Wiki Ingest

Aggiunge o aggiorna conoscenza nel wiki.

Può operare in modo **autonomo**, leggendo la cartella `raw/` senza istruzioni esplicite dell'utente, oppure seguendo indicazioni fornite in chat.

---

## Regole d'Oro dell'Ingest

1. **MAI saltare informazioni**: Ogni dato, appunto tecnico, o dettaglio presente nel source deve trovare posto nel wiki. Non decidere tu cosa è importante; è tutto importante.
2. **MAI fare riassunti riduttivi**: Se il source contiene 10 appunti tecnici su un esercizio, la pagina wiki deve contenere 10 appunti tecnici. Riorganizza, ordina, ma non eliminare.
3. **Preserva la grana del dato**: Se un appunto è espresso in modo colloquiale o specifico, mantieni quella precisione. Non "ripulire" eccessivamente se questo comporta perdita di significato.

---

Leggi `wiki/_meta/taxonomy.md` per i path. Il file istruzioni locale del vault può dichiarare override — prevale sempre sul comportamento default di questa skill.

---

## Prerequisiti

Prima di operare, leggi:

1. `wiki/_meta/hot-cache.md`
2. `wiki/_meta/index.md`
3. `wiki/_meta/taxonomy.md`

Usa sempre le skill Obsidian installate per sintassi markdown, canvas o basi.

---

## Step 1 — Leggi la cartella raw

Leggi tutti i file presenti in `raw/` (o nelle sottocartelle dichiarate dal vault).

Se l'utente ha già indicato in chat cosa fare, usa quelle informazioni come contesto aggiuntivo — ma parti comunque da `raw/`.

---

## Step 2 — Classifica il contenuto trovato

Per ogni file letto, determina a quale categoria appartiene:

### Contenuto da ingestire
Informazioni, documenti, note, articoli, audio, dataset — materiale da cui estrarre conoscenza e portare nel wiki.

Il contenuto da ingestire può richiedere due tipi di intervento diversi:

- **Contenuto genuinamente nuovo**: introduce concetti, entità o informazioni non ancora presenti nel wiki → richiede la creazione di nuove pagine
- **Contenuto aggiornato**: tratta argomenti già coperti nel wiki ma con dati più recenti, corretti o ampliati → richiede l'aggiornamento di pagine esistenti, senza creare nuovi file

Determina quale dei due casi si applica consultando `wiki/_meta/index.md` e cercando pagine con titolo simile o stesso `raw_source_path`.

### Istruzioni per il wiki
Testo scritto dall'utente che indica esplicitamente cosa fare sul wiki: "rimuovi X", "aggiorna Y", "sintetizza la sezione Z", "segna come fatto W". Queste istruzioni vengono scritte in `raw/` per comodità, come promemoria asincrono, e sono equivalenti a dirle direttamente in chat.

Non hanno un formato o naming speciale: il coding agent deve riconoscerle leggendo il contenuto. Un file è composto da istruzioni quando il suo scopo principale è **dirti cosa modificare** nel wiki, non **fornirti nuove informazioni**.

### Contenuto misto
Un file (o più file insieme) contiene sia informazioni da ingestire sia istruzioni su come modificare il wiki. Si gestisce in sequenza: prima l'ingest del contenuto, poi l'esecuzione delle istruzioni.

---

## Step 3 — Piano degli interventi e validazione

Dopo la classificazione, costruisci un piano che elenca:

- quali file contengono contenuto da ingestire (e se richiedono nuove pagine o aggiornamenti)
- quali file contengono istruzioni e un riassunto degli interventi richiesti
- l'ordine di esecuzione (contenuto misto: prima ingest, poi istruzioni)

**Validazione obbligatoria**: se il piano include l'esecuzione di istruzioni, presenta il piano all'utente e chiedi conferma prima di procedere. Usa una formulazione tipo: "Ho trovato queste istruzioni in raw/ — ho capito bene cosa fare?"

Se il piano contiene solo contenuto da ingestire senza istruzioni, puoi procedere direttamente.

---

## Step 4 — Analisi e preprocessing dei source

Prova sempre ad analizzare ogni file direttamente, qualunque sia il formato. La sequenza di fallback è:

1. **Analisi diretta**: apri e leggi il file. Se riesci a estrarre il contenuto (testo, tabelle, dati strutturati), procedi con l'ingest.
2. **wiki-preprocess**: se il formato non è analizzabile direttamente (audio, immagini senza vision, binari opachi), usa `wiki-preprocess` per trasformarlo in un formato leggibile. Per l'audio, cerca prima `<nome-audio>.transcription.md` accanto al file — se esiste, usa quello senza richiamare wiki-preprocess.
3. **Notifica all'utente**: se anche wiki-preprocess fallisce o non è in grado di trattare il formato, notifica l'utente spiegando quale file non è stato processato e perché. Non saltare mai un file silenziosamente.

L'ingest degli altri file continua normalmente — un singolo file non processabile non blocca l'intero batch.

---

## Step 5 — Ingest del contenuto

### Classificazione logica del source

Prima di procedere, determina il tipo logico:

I path reali si ricavano da `wiki/_meta/taxonomy.md`. La tabella usa i ruoli semantici.

| Tipo logico                         | Esempi                          | Azione primaria                                                              |
| ----------------------------------- | ------------------------------- | ---------------------------------------------------------------------------- |
| Articolo / web clip                 | articolo, URL salvato, clipping | Pagina ruolo `source` + pagine ruolo `knowledge` / `entity`                  |
| Documento / paper                   | PDF, paper, memo lungo          | Pagina ruolo `source` + summary esteso                                       |
| Conversazione / call                | audio, transcript, note meeting | Pagina ruolo `source` + action items verso ruolo `operation`                 |
| Idea grezza                         | nota veloce, pensiero, sketch   | Pagina ruolo `source` o `knowledge` in stato `draft`                         |
| Dataset / file strutturato          | CSV, export, tabella            | Pagina ruolo `source` + analisi verso ruolo `synthesis`                      |
| Documento immutabile di riferimento | allegato da citare              | Link o page reference, non ingest completo se il vault lo prevede            |

Mappa poi il tipo logico ai path reali del vault.

### Procedura

1. **Leggi il source completo.**
   - Documento lungo: testo prima, poi immagini solo se aggiungono contesto.

2. **Identifica il contenuto utile.**
   Cerca:
   - fatti, dati, insight
   - entità
   - concetti
   - task o azioni
   - decisioni implicite o esplicite
   - contraddizioni con pagine esistenti

3. **Check anti-duplicato.**

   Consulta `wiki/_meta/index.md` e cerca:

   - source pages esistenti con lo stesso `raw_source_path` o con titolo molto simile → se trovata, **aggiorna quella pagina** invece di crearne una nuova
   - concetti o entità che il source introduce e che già hanno una pagina → aggiorna quelle pagine, non creare duplicati
   - pagine in stato `draft` sullo stesso argomento → valuta se completarle invece di creare pagine parallele

   Se esiste già una pagina corrispondente ma il raw è **più recente** della data `updated:` della pagina esistente, trattala come aggiornamento: segnala le differenze e proponi le modifiche all'utente prima di sovrascrivere.

   Se non esiste nulla di simile, procedi a creare.

4. **Crea la source page** se il contenuto è nuovo, nel path del ruolo `source` dichiarato in `wiki/_meta/taxonomy.md`.

   Frontmatter minimo:

   ```yaml
   ---
   title: ""
   type: source
   tags: []
   raw_source_path: "raw/archived/filename"
   created: YYYY-MM-DD
   updated: YYYY-MM-DD
   confidence: low | medium | high
   status: draft
   related: []
   ---
   ```

5. **Aggiorna le pagine correlate** (path da `taxonomy.md`).
   Di solito:
   - pagine ruolo `entity` rilevanti
   - pagine ruolo `knowledge` rilevanti
   - ruolo `operation` o `list`, se emergono task
   - overview, solo se cambia lo stato generale del vault

6. **Aggiorna `wiki/_meta/index.md`** con la nuova page e le pagine toccate.

7. **Archivia il source**: sposta il file raw in `raw/archived/` (o nel path archivio dichiarato in `taxonomy.md`). Se il vault non dichiara un path archivio, crea `raw/archived/`. Aggiorna `raw_source_path` nel frontmatter della source page al nuovo path.

   La source page nel wiki **non è una copia del raw** — è una scheda strutturata che estrae, organizza e collega l'informazione. Il raw archiviato serve come riferimento al documento originale.

8. **Verifica conflitti**: forma un mini-cluster con le pagine appena create/aggiornate e le loro pagine collegate (wikilink diretti, `related:`, tag condivisi). Cerca conflitti di tipo FACTUAL, STATUS e QUANTITATIVE (vedi wiki-lint per le definizioni). Se trovi conflitti, segnalali all'utente prima di chiudere l'ingest.

9. **Verifica post-ingest**: prima di chiudere, controlla che:
   - ogni pagina creata esista al path dichiarato e abbia frontmatter valido
   - `index.md` sia aggiornato con tutte le pagine create e modificate
   - i wikilink inseriti nelle pagine nuove/aggiornate puntino a pagine esistenti
   Se qualcosa non torna, sistemalo.

10. **Appendi al log**.

---

## Step 6 — Esecuzione delle istruzioni

Da eseguire solo dopo aver ricevuto validazione dall'utente (vedi Step 3).

### Flusso

1. Identifica le pagine target dall'`index.md` o dalla richiesta.
2. Leggi le pagine interessate prima di modificarle.
3. Esegui la modifica richiesta.
4. Aggiorna `index.md` se cambia lo stato di pagine importanti.
5. Appendi al log come `update`.

### Conflict Policy

Per la procedura completa di rilevamento conflitti, vedi wiki-lint. Durante l'ingest si applica la verifica leggera dello Step 5.8. Le regole di risoluzione:

- il source con `updated:` più recente nel frontmatter vince per default
- se la pagina esistente ha `confidence: high`, segnala il conflitto all'utente prima di sovrascrivere
- registra ogni contraddizione risolta nel log

---

## Liste e area operativa

Controlla in `taxonomy.md` se i ruoli `list` e `operation` sono attivi.

Durante l'ingest:
- desideri o raccolte → ruolo `list` se attivo, altrimenti ruolo `operation`
- task e follow-up → ruolo `operation`
- contenuti da leggere/vedere → ruolo `list` se attivo

Se una lista usa `last_reviewed`, aggiornalo a ogni modifica.

---

## Fine ingest

Aggiorna `wiki/_meta/hot-cache.md` con:

- pagine create e aggiornate
- conflitti trovati: quelli risolti automaticamente (source più recente vince) e quelli segnalati all'utente
- file raw non processati (con motivo) ancora in attesa di ingest

---

## Log Format

```markdown
## [YYYY-MM-DD] ingest | Titolo source

- **Type**: article / document / call / note / data
- **Pages created**: [[slug-pagina1]], [[slug-pagina2]]
- **Pages updated**: [[slug-pagina3]]
- **Archived**: raw/archived/filename
- **Conflicts**: nessuno / descrizione (risolto / segnalato)
- **Skipped**: nessuno / file non processati con motivo
- **Notes**: osservazioni rilevanti

## [YYYY-MM-DD] update | Nome pagina aggiornata

- **Change**: descrizione della modifica
- **Pages updated**: [[slug-pagina1]], [[slug-pagina2]]
```
