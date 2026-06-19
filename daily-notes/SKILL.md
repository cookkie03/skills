---
name: daily-notes
description: >
  Processa in modo incrementale ciò che l'utente ha aggiunto al vault dall'ultimo
  ingest: daily note (_raw/daily-notes/) e nuovi source raw (_raw/articles/,
  _raw/notes/). Rileva il delta in modo deterministico, smista ogni elemento nelle
  cartelle tematiche (task→hub, conoscenza→riferimento+wikilink, link→fetch),
  archivia i source analizzati in _raw/archived/ e avanza un ledger per non
  ri-processare nulla. Usa questa skill quando l'utente dice "/daily-notes",
  "processa le daily note", "ingesta le note di oggi", "cosa ho aggiunto?",
  "guarda le note nuove", "aggiorna il vault con quello che ho scritto", o a inizio
  sessione per smaltire l'arretrato. È la versione delta e idempotente dell'ingest:
  per un ingest mirato di un singolo file fornito a mano, usa invece wiki-ingest.
---

# Daily Notes — ingest incrementale del delta utente

Smaltisce ciò che l'utente ha aggiunto da quando l'AI ha ingestato l'ultima volta:
le **daily note** e i **nuovi source raw**. Tre stadi: detection deterministica →
smistamento (con giudizio) → chiusura deterministica (archivio + ledger).

Il principio che la rende affidabile: **non ci si fida dell'autore dei commit**. Il
Stop hook fa `git add -A`, quindi un file creato dall'utente può finire in un commit
`ai:`. L'unico segnale solido è «cos'è cambiato dall'ultimo *ingest*», tracciato in
`_meta/ingest-ledger.json`. Da lì nasce l'idempotenza: rilanciarla non rifà il lavoro.

---

## Prerequisiti (leggi prima di agire)

1. `_meta/hot-cache.md` — dove eravamo
2. `_meta/taxonomy.md` — dove vanno i file (path corretti per tema)
3. Le regole del vault in `CLAUDE.md` — in particolare: `_raw/` è sacro (sola
   lettura), **non duplicare** contenuto raw nelle cartelle tematiche (si aggiungono
   riferimenti/wikilink), e `career/CareerKanban.md` è l'hub dei task di carriera.

Procedura di ingest dettagliata del vault: `_meta/procedures.md`.

---

## Step 1 — Detection (deterministico)

Dalla root del vault:

```bash
git pull --rebase --autostash 2>/dev/null || true   # incorpora i backup Obsidian
python3 .claude/skills/daily-notes/scripts/detect-pending.py --include-uncommitted
```

Restituisce un JSON con: `baseline`, `total_pending`, e tre liste — `daily_notes`
(con `added_lines` quando è un append, o `full: true` se da leggere intera),
`sources` (articoli/note), `preprocess` (file non testuali, es. audio `.m4a`).

Se `total_pending` è 0 → riferisci «niente di nuovo dall'ultimo ingest» e fermati.

---

## Step 2 — Leggi e classifica

Per le **daily note**: lavora sul delta. Se l'elemento ha `added_lines`, ragiona
**solo** su quelle righe (il resto è già stato ingestato in passato). Se ha
`full: true`, leggi l'intero file.

Per i **source** (`sources`): leggi il file completo.

Per i file in `preprocess`: invoca `wiki-preprocess` per ottenere il testo (es. la
trascrizione di un audio) e poi trattalo come un source.

Classifica ogni elemento. Le daily note sono eterogenee — un singolo file può
contenere più tipi insieme:

| Cosa hai trovato | Dove va |
|---|---|
| **Task / domanda diretta all'AI** ("ricordami di…", "scrivi a…", "verifica…") | esegui se è un'azione fattibile ora; altrimenti aggiungi all'hub giusto (task di carriera → `career/CareerKanban.md`) |
| **Conoscenza / info stabile** | pagina tematica pertinente come **riferimento sintetico + wikilink al raw** — mai copia del contenuto |
| **Link** | fetch (skill `crawl4ai`/`defuddle`) → estrai l'utile → riferimento nella pagina tematica; aggiorna `_raw/articles/Links.md` se il link veniva da lì |
| **Riflessione personale** | tema pertinente (es. pensieri); se non azionabile, lasciala dov'è |
| **Aggiornamento di stato** ("ho finito X", "ricevuto esito Y") | aggiorna la pagina/hub e, se è una milestone, appendi a `_meta/log.md` |

Se trovi una cartella corretta non ovvia, ricontrolla `_meta/taxonomy.md`.

---

## Step 3 — Applica (ibrido per tipo)

**Auto-applica senza chiedere** i casi a basso rischio e reversibili:
conoscenza → riferimento+wikilink, link → fetch+riferimento, aggiornamenti di stato.

**Chiedi conferma prima di agire** quando:
- è un **task/azione** con effetti (scrivere a qualcuno, creare file in cartelle
  nuove, candidature, modifiche a `CareerKanban.md` che cambiano priorità);
- la **classificazione è ambigua** (non sai se è una nota o un'istruzione);
- stai per **toccare un file che è in `git status`** (aperto dall'utente).

Per i casi da confermare, presenta un piano sintetico: *elemento → classificazione →
file target → azione*, e procedi su OK. Raggruppa le domande, non chiederle una a una.

Rispetta sempre: `_raw/` è di sola lettura (le daily note non si modificano mai), e
nelle cartelle tematiche vanno riferimenti, non copie del raw.

---

## Step 4 — Archivia e chiudi (deterministico)

Gli articoli/note **analizzati** vanno spostati in `_raw/archived/` (le daily note
**no**: sono continue). Poi avanza il ledger così la prossima esecuzione parte da qui.

Un solo comando fa entrambe le cose:

```bash
python3 .claude/skills/daily-notes/scripts/record-ingest.py \
  --note "daily-notes ingest <data>: <1 riga su cosa>" \
  --archive _raw/articles/<file-processato>.md _raw/notes/<altro>.md
```

- `--archive`: elenca **solo** i source davvero processati (articoli/note). Lo script
  ignora di proposito le daily note e qualsiasi path fuori da `articles/`/`notes/`.
- Senza source da archiviare (solo daily note), ometti `--archive`.

Lo script di default **committa l'ingest** (`git add -A` → commit `ai:`) e poi punta
il ledger a *quel* commit. Questo è essenziale per l'idempotenza: se il contenuto
utente era ancora non committato al momento della detection, fissare il ledger a HEAD
*prima* del commit lo farebbe ri-rilevare al giro successivo. Committando qui, la
baseline include sempre ciò che è stato appena processato. (Il file ledger, scritto
dopo il commit, lo sweepa lo Stop hook a fine turno: è fuori da `_raw/`, quindi non
genera falsi pending.)

---

## Step 5 — Riferisci

Riepiloga in chat: quante daily note / source processati, dove è finito cosa
(con wikilink), cosa è stato archiviato, e gli eventuali punti lasciati aperti o in
attesa di conferma. Se hai toccato focus/thread, aggiorna `_meta/hot-cache.md`.

---

## Perché è robusta (note di design)

- **Idempotente**: il ledger sposta la baseline in avanti a ogni ingest; rilanciarla
  non ri-processa. Gli append alle daily note si vedono come delta di righe.
- **Reversibile**: ogni effetto è dentro un commit `ai:` → undo via `git revert`/`git
  reset`. È la rete che rende sicura l'auto-applicazione dei casi a basso rischio.
- **Non invasiva sul raw**: le daily note non vengono mai modificate; l'archiviazione
  tocca solo `articles/`/`notes/` ed è un `git mv` tracciato.
- **Robusta ai conflitti con Obsidian**: `git pull --rebase` all'inizio; i file in
  `git status` si toccano solo previa conferma.
- **Autonomia graduale**: può girare on-demand, essere mostrata a inizio sessione
  (aggiungi `detect-pending.py` a `workspace-status.sh`), o essere schedulata
  (`/schedule`) come agente giornaliero una volta che ti fidi del flusso.
