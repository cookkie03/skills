---
name: workspace-setup
description: >
  Configura un vault Obsidian come workspace collaborativo AI+utente con git.
  Usa per creare un nuovo vault o allineare uno esistente: "crea vault",
  "setup workspace", "configura Obsidian Git", "prepara vault per lavorare con l'AI".
  Il risultato principale è il CLAUDE.md operativo che permette al coding agent
  di lavorare autonomamente — sia in modalità asincrona (AI riprende dopo che
  l'utente ha lavorato) sia sincrona (utente in Obsidian e AI in Claude Code
  in contemporanea).
---

# Workspace Setup

Configura il vault e genera il **CLAUDE.md**: il file che l'AI carica ad ogni
sessione e che contiene tutto il necessario per operare autonomamente senza
istruzioni extra da parte dell'utente.

Questo paradigma è indipendente da LLM Wiki: nessuna struttura `wiki/` + `raw/`,
nessun `_meta/`, nessuna pipeline di ingest. Le cartelle sono tematiche flat,
il CLAUDE.md è la fonte di verità per l'AI, git traccia chi ha fatto cosa.

---

## Differenza con wiki-init

`wiki-init` crea vault con struttura `wiki/` + `raw/` ottimizzata per l'ingest
di materiale grezzo e la generazione di pagine strutturate.

`workspace-setup` crea vault dove si lavora direttamente sui file: cartelle
tematiche flat, git come strumento operativo quotidiano, CLAUDE.md come centro
di coordinamento AI+utente.

I due paradigmi coesistono: un vault può avere sia la struttura wiki che le
cartelle workspace. In quel caso, aggiorna il CLAUDE.md esistente aggiungendo
le sezioni di questa skill.

---

## Fase 1 — Intervista (vault nuovi)

Raccogli in modo conversazionale:

1. **Scopo**: per cosa viene usato il vault?
2. **Contenuto**: che tipo di file ci sono? (note, documenti, codice, riferimenti...)
3. **Cartelle**: aree tematiche, nomi già in mente?
4. **Lingua**: italiano, inglese, mista?
5. **Remote**: GitHub o Gitea?
6. **Agent principale**: Claude, Gemini, altro? (determina il nome del file)

Per vault esistenti: rileva cosa manca ed esegui solo i passi necessari.
Proponi struttura e nomi, chiedi conferma prima di generare qualsiasi file.

---

## Fase 2 — Git

```bash
git init   # dalla root del vault, se non già presente
```

`.gitignore` nella root:

```gitignore
.obsidian/workspace.json
.obsidian/workspace-mobile.json
.obsidian/cache
.trash/
*.tmp
.DS_Store
Thumbs.db
```

Le impostazioni plugin (`.obsidian/plugins/`) e i temi rimangono versionati.

**Remote:**

GitHub:
```bash
git remote add origin git@github.com:<user>/<nome-vault>.git
# oppure con CLI: gh repo create <nome-vault> --private --source=. --remote=origin --push
```

Gitea:
```bash
git remote add origin git@<host>:<user>/<nome-vault>.git
```

**Primo commit e push:**
```bash
git add .
git commit -m "init: vault setup"
git push -u origin main
```

---

## Fase 3 — Obsidian Git plugin

**Installazione:** Settings → Community Plugins → cerca "Obsidian Git" → Install → Enable.

**Configurazione:** Settings → Obsidian Git:

| Impostazione | Valore | Perché |
|---|---|---|
| Vault backup interval (min) | `10` | auto-commit ogni 10 minuti |
| Auto pull on startup | ✅ | sincronizza all'apertura del vault |
| Push on backup | ✅ | pubblica gli auto-commit sul remote |
| Pull updates on startup | ✅ | scarica modifiche AI prima di iniziare |
| Commit message | `vault: {{date}}` | prefisso riconoscibile dall'AI |

Su mobile: se la batteria è un vincolo, usa `0` come intervallo e commita
manualmente con il pulsante nella ribbon.

---

## Fase 4 — Struttura cartelle

```
vault/
├── CLAUDE.md        ← generato nel passo successivo
├── .gitignore
├── _meta/
│   └── taxonomy.md  ← mappa dettagliata cartelle (fonte di verità per l'AI)
├── daily-notes/     ← YYYY-MM-DD.md, una per giorno
├── <tema-1>/
├── <tema-2>/
└── ...
```

`_meta/taxonomy.md` contiene la mappa estesa delle cartelle con ruoli e note.
Il CLAUDE.md include la struttura in forma compatta e rimanda a taxonomy.md
per i dettagli — così il file istruzioni resta conciso ma l'AI ha sempre
una fonte di verità completa da consultare.

---

## Fase 5 — Genera il CLAUDE.md

**Passo principale.** Compila il template con i dati reali del vault.
Nessun placeholder non compilato: il file è caricato ad ogni sessione AI
e deve essere immediatamente operativo.

Nome del file in base all'agent dichiarato nell'intervista:
- `CLAUDE.md` → Claude / Claude Code
- `AGENTS.md` → setup multi-agent o agent non specificato
- `GEMINI.md` → Gemini

---

### Template CLAUDE.md

````markdown
# [Nome Vault]

[1-2 righe: scopo, contenuto principale, lingua di lavoro.]

## Struttura

```
<cartella-1>/    # [cosa contiene]
<cartella-2>/    # [cosa contiene]
daily-notes/     # note giornaliere YYYY-MM-DD.md
_meta/           # taxonomy e metadati del vault
```

Mappa estesa con ruoli e note in `_meta/taxonomy.md`.

## Convenzione commit

| Prefisso | Autore |
|---|---|
| `vault: {{date}}` | Obsidian Git — auto-commit utente ogni ~10 min |
| `ai: <descrizione>` | AI (Claude Code) — ogni modifica fatta dall'AI |

L'AI usa sempre `ai: ` — mai `vault:`.

## A inizio sessione — sempre, prima di tutto

```bash
git pull                                  # 1. allinea allo stato più recente
git log --oneline -20                     # 2. chi ha fatto cosa e quando
git diff HEAD~3 --stat                    # 3. file toccati di recente
git status --short                        # 4. lavoro non committato (in corso adesso)
cat daily-notes/$(date +%Y-%m-%d).md     # 5. focus dichiarato dall'utente oggi
```

Dopo aver letto l'output, sintetizza ad alta voce:
- cosa ha fatto l'utente (`vault:` commits) dall'ultima sessione AI
- cosa è già stato fatto dall'AI (`ai:` commits) nelle sessioni precedenti
- task aperti (`- [ ]`) e menzioni rilevanti nella daily note di oggi
- se l'utente è attivo adesso: `git status` non vuoto → file aperti in Obsidian

Poi aspetta la richiesta, oppure proponi un'azione concreta basata su quanto trovato.

**Come leggere l'output:**
- `vault:` nel log → lavoro utente; i file toccati mostrano il focus recente
- `ai:` nel log → lavoro AI precedente; la descrizione dice cosa è già fatto
- file in `git status --short` → in modifica negli ultimi minuti, probabilmente
  aperti in Obsidian adesso — non toccarli senza chiedere
- daily note assente per oggi → chiedi all'utente su cosa vuole lavorare

## Durante la sessione

**Prima di leggere qualsiasi file:**
```bash
git pull   # incorpora gli auto-commit di Obsidian Git degli ultimi minuti
```

**Prima di ogni commit:**
```bash
git pull                            # evita conflitti con auto-commit Obsidian
git add <file>
git commit -m "ai: <descrizione>"
git push
```

Se il pull genera un conflitto: risolvi preferendo la versione con mtime
più recente, salvo indicazioni diverse dell'utente.

**Se durante la sessione compaiono nuovi file in `git status --short`:**
L'utente ha iniziato a editare qualcosa in Obsidian — non toccare quei file
senza richiesta esplicita.

## Regole operative

- Prima di creare file: guarda la struttura sopra e scegli la cartella giusta.
- Non creare cartelle senza accordo esplicito con l'utente.
- Non modificare file senza richiesta esplicita o accordo nella sessione.
- File in `git status --short` = in uso attivo dall'utente.
- Preferisci modificare file esistenti piuttosto che crearne di nuovi.
- [Regole specifiche di questo vault — aggiungere qui]

## Skill per operazioni specializzate

| Operazione | Skill |
|---|---|
| Preprocessing audio, immagini, documenti Office | `wiki-preprocess` |
| Crawling e ingest di URL | `crawl4ai` |
| Sintassi Obsidian (wikilinks, callout, frontmatter) | `obsidian-markdown` |
| File .base (database view di note) | `obsidian-bases` |
| File .canvas (mappe, diagrammi) | `json-canvas` |
| Artefatti visivi (canvas, Dataview, kanban) | `wiki-artifact` |
| Health check del vault | `wiki-lint` |

[Rimuovi le righe non rilevanti per questo vault.]
````

---

## Template `_meta/taxonomy.md`

Genera questo file insieme al CLAUDE.md. È la fonte di verità estesa per la
struttura del vault — il CLAUDE.md la richiama, l'AI la legge prima di creare
file in cartelle non ovvie.

```markdown
---
vault_name: ""
language: it | en
---

# Taxonomy

| Cartella | Contenuto | Note |
|---|---|---|
| daily-notes/ | Note giornaliere (YYYY-MM-DD.md) | |
| <tema-1>/ | ... | |
| <tema-2>/ | ... | |
| _meta/ | Taxonomy e metadati del vault | Non creare note di lavoro qui |
```

Compila con le cartelle reali emerse dall'intervista. Aggiorna quando si
aggiungono cartelle nuove.

---

## Script di orientamento

Lo script `scripts/workspace-status.sh` (incluso in questa skill) esegue
i comandi di orientamento in un colpo solo e può essere invocato dal CLAUDE.md:

```bash
bash <percorso-skill>/scripts/workspace-status.sh
```

Stampa: commit recenti con legenda vault/ai, file toccati, modifiche non
committate, daily note di oggi. Funziona su vault con qualsiasi struttura
di cartelle.
