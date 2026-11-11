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

1. **MAI saltare informazioni**: ogni dato, appunto tecnico, o dettaglio presente nel source deve trovare posto nel wiki. Non decidere tu cosa è importante; è tutto importante.
2. **MAI fare riassunti riduttivi**: se il source contiene 10 appunti tecnici su un esercizio, la pagina wiki deve contenere 10 appunti tecnici. Riorganizza, ordina, ma non eliminare.
3. **Preserva la grana del dato**: se un appunto è espresso in modo colloquiale o specifico, mantieni quella precisione. Non "ripulire" eccessivamente se questo comporta perdita di significato.

---

Leggi `_meta/taxonomy.md` per i path. Il file istruzioni locale del vault può dichiarare override — prevale sempre sul comportamento default di questa skill.

---

## Prerequisiti

Prima di operare, leggi:

1. `_meta/hot-cache.md`
2. `_meta/index.md`
3. `_meta/taxonomy.md`

Usa sempre le skill Obsidian installate per sintassi markdown, canvas o basi.

---

## Step 1 — Leggi la cartella raw

Leggi tutti i file presenti in `raw/` (o nelle sottocartelle dichiarate dal vault), **escludendo `raw/archived/`**: quella cartella contiene file già processati (source ingestiti o istruzioni già eseguite) e non va riletta. Se l'archiviazione funziona, questa cartella si "auto-pulisce" run dopo run — non serve un check separato per evitare doppioni grossolani.

Se l'utente ha già indicato in chat cosa fare, usa quelle informazioni come contesto aggiuntivo — ma parti comunque da `raw/`.

---

## Step 2 — Classifica il contenuto trovato

Per ogni file letto, determina a quale categoria appartiene:

### Contenuto da ingestire

Informazioni, documenti, note, articoli, audio, dataset — materiale da cui estrarre conoscenza e portare nel wiki.

Il contenuto da ingestire può richiedere due tipi di intervento diversi:

- **Contenuto genuinamente nuovo**: introduce concetti, entità o informazioni non ancora presenti nel wiki → richiede la creazione di nuove pagine
- **Contenuto aggiornato**: tratta argomenti già coperti nel wiki ma con dati più recenti, corretti o ampliati → richiede l'aggiornamento di pagine esistenti, senza creare nuovi file

Determina quale dei due casi si applica consultando `_meta/index.md` e cercando pagine con titolo simile o stesso `raw_source_path`.

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

## Step 4 — Preprocessing dei source

Prima di leggere un source, verifica se richiede preprocessing:

- **Audio**: cerca il file di trascrizione dichiarato dal vault (default: `<nome-audio>.transcription.md` accanto al file). Se esiste, usa quello. Se non esiste, attiva `wiki-preprocess`.
- **Immagini**: descrivi il contenuto se il modello ha vision; altrimenti segnala che serve descrizione manuale.
- **Tutti gli altri formati**: leggili direttamente o usa la skill specializzata più adatta, come `pdf`.

Se il file ha un formato non supportato, non chiaramente leggibile, o non facilmente ingestabile in modo affidabile, non forzare l'ingest diretto: passa prima da `wiki-preprocess`.

---

## Step 5 — Ingest del contenuto

### Classificazione logica del source

Prima di procedere, determina il tipo logico:

I path reali si ricavano da `_meta/taxonomy.md`. La tabella usa i ruoli semantici.

| Tipo logico                         | Esempi                          | Azione primaria                                                   |
| ----------------------------------- | -------------------------------- | ------------------------------------------------------------------ |
| Articolo / web clip                 | articolo, URL salvato, clipping  | Pagina ruolo `source` + pagine ruolo `knowledge` / `entity`        |
| Documento / paper                   | PDF, paper, memo lungo           | Pagina ruolo `source` + summary esteso                             |
| Conversazione / call                | audio, transcript, note meeting  | Pagina ruolo `source` + action items verso ruolo `operation`       |
| Idea grezza                         | nota veloce, pensiero, sketch    | Pagina ruolo `source` o `knowledge` in stato `draft`               |
| Dataset / file strutturato          | CSV, export, tabella             | Pagina ruolo `source` + analisi verso ruolo `synthesis`            |
| Documento immutabile di riferimento | allegato da citare               | Link o page reference, non ingest completo se il vault lo prevede  |

Mappa poi il tipo logico ai path reali del vault.

### Procedura

1. **Leggi il source completo.**
   - Documento lungo: testo prima, poi immagini solo se aggiungono contesto.
2. **Identifica il contenuto utile.**
   Cerca:
   - fatti, dati, insight
   - entità
   - concetti
   - task o azioni (se emergono, vanno verso ruolo `operation`/`list` — vedi sotto)
   - decisioni implicite o esplicite
   - contraddizioni con pagine esistenti
3. **Check anti-duplicato.**

   Consulta `_meta/index.md` e cerca:

   - source pages esistenti con lo stesso `raw_source_path` o con titolo molto simile → se trovata, **aggiorna quella pagina** invece di crearne una nuova
   - concetti o entità che il source introduce e che già hanno una pagina → aggiorna quelle pagine, non creare duplicati
   - pagine in stato `draft` sullo stesso argomento → valuta se completarle invece di creare pagine parallele

   Se esiste già una pagina corrispondente ma il raw è **più recente** della data `updated:` della pagina esistente, trattala come aggiornamento: segnala le differenze e proponi le modifiche all'utente prima di sovrascrivere.

   Se non esiste nulla di simile, procedi a creare.
4. **Crea la source page** se il contenuto è nuovo, nel path del ruolo `source` dichiarato in `_meta/taxonomy.md`.

   Frontmatter minimo:

   ```yaml
   ---
   title: ""
   type: source
   tags: []
   raw_source_path: "raw/filename"
   created: YYYY-MM-DD
   updated: YYYY-MM-DD
   confidence: low | medium | high
   status: draft
   related: []
   ---
   ```
5. **Aggiorna le pagine correlate** (path da `taxonomy.md`). Di solito:
   - pagine ruolo `entity` rilevanti
   - pagine ruolo `knowledge` rilevanti
   - ruolo `operation` o `list`, se emergono task, desideri o raccolte (controlla in `taxonomy.md` quali dei due ruoli sono attivi nel vault; se una `list` usa `last_reviewed`, aggiornalo)
   - overview, solo se cambia lo stato generale del vault

Quando hai finito con tutti i file da ingestire, vai allo **Step 7 — Chiusura**.

---

## Step 6 — Esecuzione delle istruzioni

Da eseguire solo dopo aver ricevuto validazione dall'utente (vedi Step 3).

1. Identifica le pagine target dall'`index.md` o dalla richiesta.
2. Leggi le pagine interessate prima di modificarle.
3. Esegui la modifica richiesta.

### Conflict Policy

Se il nuovo contenuto contraddice una pagina esistente:

- il source con `updated:` più recente nel frontmatter vince per default
- se la pagina esistente ha `confidence: high`, segnala il conflitto prima di sovrascrivere
- registra ogni contraddizione risolta nel log (Step 7)

Quando hai finito con tutte le istruzioni, vai allo **Step 7 — Chiusura**.

---

## Step 7 — Chiusura

Eseguita una volta alla fine del run, indipendentemente dal fatto che si arrivi dallo Step 5, dallo Step 6, o da entrambi (contenuto misto). Per ogni file di `raw/` effettivamente processato in questo run:

1. **Sposta il file in `raw/archived/`**, se questo ruolo è attivo in `_meta/taxonomy.md` — vale sia per i source ingestiti (Step 5) sia per i file di istruzioni eseguiti (Step 6). Aggiorna `raw_source_path` nella pagina collegata con il nuovo percorso. Spostare fisicamente il file evita che lo Step 1 lo rilegga e lo ri-elabori ai run successivi (cruciale per l'uso autonomo della skill). Se il vault non usa `raw/archived/`, lascia i file dove sono.
2. **Aggiorna `_meta/index.md`** con le pagine create/aggiornate.
3. **Aggiorna `_meta/hot-cache.md`** con: pagine create e aggiornate, contraddizioni risolte, pending ingest ancora aperti.
4. **Appendi al log** (formato sotto): una entry `ingest` per ogni source ingestito, una entry `update` per ogni istruzione eseguita.

---

## Log Format

```markdown
## [YYYY-MM-DD] ingest | Titolo source

- **Type**: article / document / call / note / data
- **Pages created**: [[sources/slug]], [[concepts/nome]]
- **Pages updated**: [[entities/nome]], [[ops/pagina]]
- **Contradictions**: nessuna / descrizione
- **Notes**: osservazioni rilevanti

## [YYYY-MM-DD] update | Nome pagina aggiornata

- **Change**: descrizione della modifica
- **Pages updated**: [[pagina1]], [[pagina2]]
```
