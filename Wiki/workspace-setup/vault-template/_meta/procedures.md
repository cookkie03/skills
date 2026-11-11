# Procedures

Procedure operative dettagliate. Lette su richiesta — non necessarie ad ogni sessione.

## File di stato vivi

| File | Ruolo | Aggiornato da |
|---|---|---|
| `taxonomy.md` | Mappa cartelle → contenuto | AI (manuale, quando si crea una cartella) |
| `index.md` | Catalogo contenuti del vault | sync.py (automatico a fine turno AI) |
| `hot-cache.md` | Contesto caldo: focus e thread aperti | AI (semantica) + sync.py (file toccati) |
| `log.md` | Storia del perché: decisioni, milestone | AI (manuale, append-only) |

## Delta utente a inizio messaggio (`session-brief.sh`)

A ogni messaggio l'hook di pre-turno (`_meta/session-brief.sh`, cablato come
`UserPromptSubmit` in `.claude/settings.json`) inietta nel contesto il **delta
dall'ultimo commit `ai:`**: commit `vault:`, file non committati, risorse nuove in
`_raw/`, commenti `%%` nelle pagine cambiate. È read-only e silenzioso quando non
c'è delta (subito dopo un commit `ai:` il range è vuoto). Quando NON è vuoto:

- È la fotografia di cosa ha fatto l'utente mentre l'AI non c'era. Leggila prima
  di agire: potrebbe aver già risolto, spostato o corretto qualcosa.
- Riconcilia lo stato vivo se necessario: `index.md` si rigenera da solo, ma
  `taxonomy.md` (nuove cartelle), `log.md` (decisioni dell'utente degne di nota) e
  i `Thread aperti` di `hot-cache.md` potrebbero andare aggiornati.
- Processa l'inbox `_raw/` e i commenti `%%` (sotto).

Esecuzione manuale: `bash _meta/session-brief.sh`.

## Commenti `%%` (istruzioni inline dell'utente)

In Obsidian `%% … %%` è un commento invisibile in lettura. L'utente lo usa per
lasciare istruzioni all'AI dentro la pagina ("%% espandi questa sezione %%",
"%% questa fonte è da verificare %%"). Trattali come richieste dirette:

- Esegui ciò che chiedono nel contesto della pagina in cui stanno.
- Poi **risolvili**: rimuovi il commento se l'istruzione è completata, oppure
  rispondi inline e lascialo solo se serve ancora una decisione dell'utente.
- Non lasciare `%%` orfani: un commento già evaso che resta confonde i turni
  successivi (verrebbe rifatto). Se non sei sicuro dell'intento, chiedi invece
  di indovinare.
- I commenti `%%` possono essere inline o di blocco (multi-riga: `%%` su una riga,
  testo, `%%` su un'altra). `session-brief.sh` segnala le righe con `%%`; apri il
  file per leggere il blocco completo.

## Inbox `_raw/`

`_raw/` è la cartella dove l'utente deposita risorse grezze da integrare (file
scaricati, appunti, export, audio/immagini/Office). È esclusa da index e
validazione frontmatter. Ciclo di lavorazione:

- Se il file non è testo leggibile (audio, immagine, .docx/.pptx/.xlsx, PDF):
  prima `wiki-preprocess` per convertirlo/descriverlo.
- Poi `wiki-ingest` per integrarne il contenuto nelle pagine giuste del vault
  (usa `taxonomy.md` per decidere dove).
- A integrazione avvenuta, **svuota** la risorsa da `_raw/`: spostala in archivio
  o eliminala, così l'inbox segnala solo ciò che resta da fare. Registra in
  `log.md` solo se l'ingest ha prodotto una decisione o una pagina significativa.

## Come leggere il git log

- `vault: ...` → auto-commit Obsidian (utente ha lavorato in quell'intervallo di tempo)
- `ai: ...` → turno AI completato; la descrizione dice cosa è stato fatto
- File in `git status --short` → in modifica adesso, probabilmente aperti in Obsidian

## Durante la sessione

- Prima di leggere un file: `git pull` (incorpora auto-commit Obsidian degli ultimi minuti).
- Prima di committare manualmente: `git pull` per evitare conflitti con Obsidian Git.
- Se il pull genera conflitti: preferisci la versione con mtime più recente, salvo
  indicazioni diverse dell'utente.

## Mantenere CLAUDE.md immutabile

CLAUDE.md contiene solo regole stabili. Lo script `_meta/check-claude-md.py`
verifica meccanicamente che non accumuli contenuto che invecchia, e gira da solo
a inizio sessione (`workspace-status.sh`) e nel hook auto-commit quando CLAUDE.md
cambia. Se segnala qualcosa, sposta il contenuto nel file vivo giusto:

- **Date / fatti datati** → `_meta/log.md`
- **Procedure passo-passo** → `_meta/procedures.md` (in CLAUDE.md solo una riga di rimando)
- **Cataloghi / liste lunghe** → `_meta/index.md` o `taxonomy.md`
- **Path inesistenti** → rename non propagato: aggiorna i riferimenti

Esecuzione manuale: `python3 _meta/check-claude-md.py` (aggiungi `--strict` per
exit 1 sui problemi, utile in un pre-commit).

## Validazione frontmatter (`check-frontmatter.py`)

`_meta/check-frontmatter.py` controlla che le pagine abbiano un frontmatter
coerente con lo schema dichiarato in `taxonomy.md` (blocco `# frontmatter-schema`).
Segnala: pagine senza frontmatter, campi obbligatori mancanti per famiglia, valori
`type`/`status` fuori enum, tag non registrati in `taxonomy.md`. È data-driven: se
aggiorni le famiglie in `taxonomy.md`, il validatore si adegua da solo.

- Esecuzione: `python3 _meta/check-frontmatter.py` (warn-only) · `--strict` (exit 1) ·
  `--fix` (registra in `taxonomy.md` i soli tag ricorrenti non ancora elencati — unico
  auto-fix sicuro; date/type/status mancanti restano da sistemare a mano).
- Gira nel hook `auto-commit.sh` (warn-only, solo se cambiano .md nel turno) e a inizio
  sessione via `workspace-status.sh`.
- Esclude `_raw/`, `_models/`, `_meta/`, `_scratch/` e ogni cartella che inizia per `.`.

## Rinominare o spostare una cartella

Un rename non propagato lascia riferimenti rotti sparsi. Procedura:

1. `grep -rn "vecchio-nome" _meta/ CLAUDE.md` e aggiorna ogni riferimento.
2. Aggiorna `_meta/taxonomy.md` con la nuova struttura.
3. Registra il rename in `_meta/log.md` (tipo `refactor`) — **mai** in CLAUDE.md.
4. `python3 _meta/check-claude-md.py` per confermare che non resti nessun path rotto.

## File toccati di recente (NON editare a mano)

La sezione "File toccati di recente" in `hot-cache.md` la riscrive `sync.py` a ogni
turno (cappata alle ultime ~10 voci dai commit `ai:`). Qualsiasi modifica manuale
viene sovrascritta: non perderci tempo. Le sezioni "Focus corrente" e "Thread
aperti" sono invece tue — quelle aggiornale a mano.

## Formato `_meta/hot-cache.md`

Finestra mobile: sovrascrivi le voci superate, tienilo corto.

```markdown
# Hot Cache

**Aggiornato**: YYYY-MM-DD

## Focus corrente
- [su cosa si sta lavorando / dove si è arrivati]

## Thread aperti
- [ ] [cosa resta aperto per la prossima sessione]

## File toccati di recente
- [[...]]    ← auto-aggiornato da sync.py
```

## Formato `_meta/log.md`

Append-only. Una voce per evento significativo.

```markdown
## [YYYY-MM-DD] <tipo> | <titolo breve>
- [cosa è successo e perché, 1-2 righe]
```

Tipi: `decision` · `milestone` · `conflict-resolved` · `refactor` · `init`
