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

## Contratto comune

Questa skill deve funzionare bene in vault di progetto, second brain, wiki di ricerca e setup ibridi.

Assumi sempre che il file istruzioni locale del vault sia già nel contesto e possa dichiarare:

- mapping cartelle raw (`raw/papers` vs `raw/pdfs`, `raw/audio` vs `raw/calls`)
- uso o non uso di `daily-notes/`
- presenza di `wiki/lists/`, `wiki/ops/`, `wiki/build/`, `wiki/artifacts/`
- tipi pagina canonici e policy locali

Se il comportamento standard della skill e il contratto locale del vault sono in conflitto, vince il contratto locale.

Ragiona prima per categorie logiche:

- source grezzi
- pagine knowledge
- area operativa
- decisioni
- artifact

Solo dopo mappa queste categorie ai path reali del vault.

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

## Step 4 — Preprocessing dei source

Prima di leggere un source, verifica se richiede preprocessing:

- **Audio**: se esiste un file `.transcription.md` accanto all'audio, usa quello. Se non esiste, usa `wiki-preprocess` o segnala che serve il preprocessing audio dichiarato dal vault.
- **Immagini**: descrivi il contenuto se il modello ha vision; altrimenti segnala che serve descrizione manuale.
- **Tutti gli altri formati**: leggili direttamente o usa la skill specializzata più adatta, come `pdf`.

Se il file ha un formato non supportato, non chiaramente leggibile, o non facilmente ingestabile in modo affidabile, non forzare l'ingest diretto: passa prima da `wiki-preprocess`.

---

## Step 5 — Ingest del contenuto

### Classificazione logica del source

Prima di procedere, determina il tipo logico:

| Tipo logico                         | Esempi                          | Azione primaria                                                   |
| ----------------------------------- | ------------------------------- | ----------------------------------------------------------------- |
| Articolo / web clip                 | articolo, URL salvato, clipping | Source page + concepts/entities                                   |
| Documento / paper                   | PDF, paper, memo lungo          | Source page + summary esteso                                      |
| Conversazione / call                | audio, transcript, note meeting | Source page + action items verso area operativa                   |
| Idea grezza                         | nota veloce, pensiero, sketch   | Source o concept `draft`                                          |
| Dataset / file strutturato          | CSV, export, tabella            | Source page + analisi -> synthesis                                |
| Documento immutabile di riferimento | allegato da citare              | Link o page reference, non ingest completo se il vault lo prevede |

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

4. **Crea la source page** se il contenuto è nuovo, nell'area sources del vault, di default `wiki/sources/<slug>.md`.

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

5. **Aggiorna le pagine correlate**.
   Di solito:
   - entità rilevanti
   - concetti chiave
   - area operativa o liste, se emergono task
   - overview, solo se cambia lo stato generale del vault

6. **Aggiorna `wiki/_meta/index.md`** con la nuova page e le pagine toccate.

7. **Archivia il source** se il vault usa `raw/archived/`. Registra l'ingest senza spostarle.

8. **Appendi al log**.

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

Se il nuovo contenuto contraddice una pagina esistente:

- il source più recente vince per default
- se la pagina esistente ha `confidence: high`, segnala il conflitto prima di sovrascrivere
- registra ogni contraddizione risolta nel log

---

## Liste e area operativa

Se il vault ha `wiki/lists/`, tratta le liste come pagine first-class.
Se il vault non ha `wiki/lists/`, instrada gli item pratici verso l'area operativa equivalente, di solito `wiki/ops/`.

Durante l'ingest:

- desideri o raccolte -> liste dedicate se esistono
- task e follow-up -> lista task o area ops del vault
- contenuti da leggere/vedere -> reading list se esiste

Se una lista usa `last_reviewed`, aggiornalo a ogni modifica.

---

## Fine ingest

Aggiorna `wiki/_meta/hot-cache.md` con:

- pagine create e aggiornate
- contraddizioni risolte
- pending ingest ancora aperti

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
