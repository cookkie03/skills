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

Configura il vault e genera due cose distinte:

1. **CLAUDE.md** — istruzioni operative, scritte una volta e **non più modificate**.
   È il file che l'AI carica ad ogni sessione: dice come lavorare, dove guardare,
   come committare.
2. **File di stato vivi** in `_meta/` — la memoria del vault, che l'AI **tiene
   sempre aggiornata** mentre lavora (come nel paradigma wiki).

Questa separazione è il cuore della skill: CLAUDE.md è immutabile e contiene
le *regole*; i file in `_meta/` sono lo *stato* e cambiano nel tempo. CLAUDE.md
non contiene cataloghi o liste che invecchiano — rimanda ai file vivi.

Questo paradigma è indipendente da LLM Wiki: nessuna struttura `wiki/` + `raw/`,
nessuna pipeline di ingest. Le cartelle sono tematiche flat, git traccia chi ha
fatto cosa, i file `_meta/` danno la mappa semantica e il contesto che git non ha.

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

## I file di stato vivi (`_meta/`)

Quattro file che l'AI consulta e mantiene. Sono la memoria del vault: git
registra *cosa* è cambiato e *quando*, questi file dicono *perché*, *dov'è* e
*qual è il filo del discorso*.

| File | Ruolo | Chi legge | Chi aggiorna |
|---|---|---|---|
| `taxonomy.md` | Mappa cartelle → ruolo/contenuto. Fonte di verità per dove creare file. | prima di creare file | quando si aggiungono cartelle |
| `index.md` | Catalogo dei contenuti: file/note → di cosa trattano. Evita duplicati, fa trovare il file giusto senza scansionare tutto. | per orientarsi sui contenuti | a ogni file creato/rilevante modificato |
| `hot-cache.md` | Contesto caldo: aree toccate di recente, thread aperti, focus corrente. Letto **per primo** a inizio sessione per orientarsi in fretta. | a inizio sessione | a fine sessione |
| `log.md` | Registro cronologico append-only degli eventi significativi (decisioni, milestone, conflitti risolti). Leggibile da umano e AI. | quando serve la storia del *perché* | dopo ogni cambiamento significativo |

Razionale dell'adattamento dal paradigma wiki:

- `index.md` e `hot-cache.md` hanno lo stesso scopo che hanno in `wiki-query`
  e `wiki-ingest`: orientarsi velocemente senza rileggere tutto il vault.
- `log.md` complementa i commit automatici `vault: {{date}}` di Obsidian Git,
  che sono mute timestamp: il log dice il *perché* dietro i cambiamenti.
- `taxonomy.md` è la stessa fonte di verità sui path usata da tutte le skill wiki-*.

Tieni i file leggeri: `hot-cache.md` è una finestra mobile (sovrascrivi le voci
vecchie), `log.md` è append-only ma sintetico, `index.md` una riga per voce.

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

## Fase 3b — Hook Claude Code (auto-commit AI)

Claude Code supporta un hook `Stop` che scatta alla fine di ogni turno.
Con questo hook il vault si auto-committa dopo ogni risposta dell'AI, con
prefisso `ai:` — senza che l'AI debba ricordarselo.

Copia i file dalla cartella `vault-template/` di questa skill nel vault:

```
vault-template/
├── _meta/
│   └── sync.py                     → _meta/sync.py
└── .claude/
    ├── settings.json               → .claude/settings.json
    └── hooks/
        └── auto-commit.sh          → .claude/hooks/auto-commit.sh
```

Oppure crea i file manualmente seguendo i template in `vault-template/`.

Dopo la copia:
```bash
chmod +x .claude/hooks/auto-commit.sh
```

**`.claude/settings.json`** — se il file esiste già, aggiungi solo il blocco
`Stop` dentro `hooks` senza sovrascrivere le altre impostazioni:

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "bash .claude/hooks/auto-commit.sh"
          }
        ]
      }
    ]
  }
}
```

Aggiungi `.claude/` e `_meta/sync.py` al commit iniziale del vault.

**Cosa ottieni a fine ogni turno AI (in automatico):**

| Operazione | Come |
|---|---|
| `_meta/index.md` ricostruito | `sync.py` scansiona tutti i .md del vault |
| `_meta/hot-cache.md` "File toccati" aggiornato | `sync.py` legge gli ultimi commit `ai:` |
| Modifiche committate con `ai:` | `auto-commit.sh` dopo sync |
| Push sul remote | `auto-commit.sh` |

**Cosa rimane all'AI (non automatizzabile meccanicamente):**

- `_meta/hot-cache.md` — sezioni "Focus corrente" e "Thread aperti": l'AI le
  aggiorna dopo ogni cambiamento di focus (vedi istruzioni nel CLAUDE.md)
- `_meta/log.md` — l'AI appende una voce dopo decisioni e milestone
- `_meta/taxonomy.md` — aggiornato quando si crea una nuova cartella

---

## Fase 4 — Struttura cartelle

```
vault/
├── CLAUDE.md          ← istruzioni immutabili (generato nel passo successivo)
├── .gitignore
├── .claude/
│   ├── settings.json  ← Stop hook per auto-commit AI
│   └── hooks/
│       └── auto-commit.sh
├── _meta/             ← file di stato vivi, mantenuti dall'AI
│   ├── taxonomy.md    ← mappa cartelle → ruolo/contenuto
│   ├── index.md       ← catalogo dei contenuti (auto-rebuild da sync.py)
│   ├── hot-cache.md   ← contesto caldo (file toccati auto, focus manuale)
│   ├── log.md         ← registro eventi significativi (manuale)
│   └── sync.py        ← aggiorna index e hot-cache (chiamato dallo Stop hook)
├── daily-notes/       ← YYYY-MM-DD.md, una per giorno
├── <tema-1>/
├── <tema-2>/
└── ...
```

I quattro file in `_meta/` sono descritti nella sezione "I file di stato vivi".
Il CLAUDE.md non duplica il loro contenuto: vi rimanda. Così resta immutabile
mentre lo stato del vault evolve nei file vivi.

---

## Fase 5 — Genera il CLAUDE.md e i file di stato

Genera il CLAUDE.md **e** i quattro file `_meta/` insieme: il CLAUDE.md fa
riferimento ai file vivi, quindi devono esistere fin dall'inizio (anche se
inizialmente quasi vuoti).

Compila il template con i dati reali del vault. Nessun placeholder non compilato:
il file è caricato ad ogni sessione AI e deve essere immediatamente operativo.

Il CLAUDE.md va scritto **una volta sola**. Non contiene cataloghi, liste o
stato che invecchiano — quelli vivono in `_meta/` e li aggiorna l'AI durante
il lavoro. Se in futuro serve cambiare *le regole*, allora sì si tocca il
CLAUDE.md; ma il flusso normale di lavoro non lo modifica mai.

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
_meta/           # file di stato vivi (vedi sotto)
```

Mappa estesa con ruoli e note in `_meta/taxonomy.md`.

## File di stato vivi — leggere e tenere aggiornati

Sono la memoria del vault. Consultali per orientarti, aggiornali quando lavori.

| File | A cosa serve | Quando aggiornarlo |
|---|---|---|
| `_meta/taxonomy.md` | Dove vivono i contenuti (cartella → ruolo) | quando aggiungi una cartella |
| `_meta/index.md` | Catalogo: quali contenuti esistono e di cosa trattano | quando crei un file o ne modifichi uno in modo rilevante |
| `_meta/hot-cache.md` | Contesto caldo: su cosa si sta lavorando ora | a fine sessione, con le aree toccate |
| `_meta/log.md` | Storia del *perché*: decisioni, milestone | dopo un cambiamento significativo |

Questi file, non il CLAUDE.md, sono la fonte di verità sullo stato corrente.

## Convenzione commit

| Prefisso | Autore |
|---|---|
| `vault: {{date}}` | Obsidian Git — auto-commit utente ogni ~10 min |
| `ai: <descrizione>` | AI (Claude Code) — ogni modifica fatta dall'AI |

L'AI usa sempre `ai: ` — mai `vault:`.

## A inizio sessione — sempre, prima di tutto

```bash
git pull                                  # 1. allinea allo stato più recente
cat _meta/hot-cache.md                    # 2. contesto caldo: dove eravamo
cat _meta/index.md                        # 3. catalogo dei contenuti del vault
git log --oneline -20                     # 4. chi ha fatto cosa e quando
git diff HEAD~3 --stat                    # 5. file toccati di recente
git status --short                        # 6. lavoro non committato (in corso adesso)
cat daily-notes/$(date +%Y-%m-%d).md     # 7. focus dichiarato dall'utente oggi
```

`hot-cache.md` ti dà il filo del discorso in pochi token; `index.md` ti dice
cosa esiste nel vault; git e la daily note ti dicono cosa è cambiato di recente.

Dopo aver letto l'output, sintetizza ad alta voce:
- dove eravamo rimasti (da `hot-cache.md`)
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

**Quando crei o modifichi contenuti in modo rilevante:**
- aggiorna `_meta/index.md` con la voce nuova/cambiata
- se hai preso una decisione o raggiunto una milestone, appendi a `_meta/log.md`

## A fine sessione

`_meta/index.md` e la sezione "File toccati" di `hot-cache.md` vengono
aggiornati **automaticamente** dallo Stop hook (sync.py + auto-commit).

**Quello che devi fare tu (parte semantica):**

**1. Aggiorna `_meta/hot-cache.md` — Focus e Thread:**
```markdown
## Focus corrente
- [su cosa si è lavorato / dove siamo arrivati]

## Thread aperti
- [ ] [cosa resta aperto per la prossima sessione]
```
Sovrascrivi le voci superate — tienilo corto, è una finestra mobile.

**2. Se è successo qualcosa di significativo, appendi a `_meta/log.md`:**
```markdown
## [YYYY-MM-DD] <tipo> | <titolo breve>
- [cosa è successo e perché, 1-2 righe]
```
Tipi comuni: `decision`, `milestone`, `conflict-resolved`, `refactor`.

**3. Se hai creato una nuova cartella, aggiorna `_meta/taxonomy.md`.**

Il commit finale è automatico: lo Stop hook committa e pusha tutto, incluse
le modifiche ai meta file appena fatti.

## Regole operative

- Prima di creare file: leggi `_meta/taxonomy.md` e scegli la cartella giusta.
- Non creare cartelle senza accordo esplicito con l'utente.
- Non modificare file senza richiesta esplicita o accordo nella sessione.
- File in `git status --short` = in uso attivo dall'utente.
- Preferisci modificare file esistenti piuttosto che crearne di nuovi.
- Tieni aggiornati i file `_meta/` — sono la memoria condivisa con l'utente.
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

## Template `_meta/index.md`

Catalogo dei contenuti. A setup è quasi vuoto; cresce man mano che il vault
si popola. Una riga per voce, raggruppata per cartella.

```markdown
# Index

Catalogo dei contenuti del vault. Aggiornato dall'AI a ogni file rilevante
creato o modificato. Una riga per voce.

## <tema-1>/
- [[<tema-1>/nota-esempio]] — di cosa tratta in una riga

## <tema-2>/
-
```

---

## Template `_meta/hot-cache.md`

Contesto caldo: finestra mobile su dove si sta lavorando. Sovrascrivibile,
sempre corto.

```markdown
# Hot Cache

Contesto di lavoro recente. Finestra mobile: le voci vecchie si sovrascrivono.
Letto a inizio sessione per riprendere il filo.

**Aggiornato**: YYYY-MM-DD

## Focus corrente
- [su cosa stiamo lavorando]

## Thread aperti
- [ ] [cosa è in sospeso]

## File toccati di recente
- [[...]]
```

---

## Template `_meta/log.md`

Registro append-only degli eventi significativi. Non si riscrive: si appende.

```markdown
# Log

Registro cronologico degli eventi significativi del vault (decisioni,
milestone, conflitti risolti). Append-only, sintetico.

## [YYYY-MM-DD] init
- Vault creato con workspace-setup.
```

Voci successive seguono lo stesso formato:

```markdown
## [YYYY-MM-DD] <tipo> | <titolo breve>
- [cosa è successo e perché, 1-2 righe]
```

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
