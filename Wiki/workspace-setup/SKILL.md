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

1. **CLAUDE.md** — istruzioni operative, scritte una volta e **non più modificate**. È il file che l'AI carica ad ogni sessione: dice come lavorare, dove guardare, come committare.
2. **File di stato vivi** in `_meta/` — la memoria del vault, che l'AI **tiene sempre aggiornata** mentre lavora.

Questa separazione è il cuore della skill: CLAUDE.md è immutabile e contiene le *regole*; i file in `_meta/` sono lo *stato* e cambiano nel tempo. CLAUDE.md non contiene cataloghi o liste che invecchiano — rimanda ai file vivi.

---

## I file di stato vivi (`_meta/`)

Quattro file che l'AI consulta e mantiene. Sono la memoria del vault: git registra *cosa* è cambiato e *quando*, questi file dicono *perché*, *dov'è* e *qual è il filo del discorso*.

| File | Ruolo | Chi legge | Chi aggiorna |
|---|---|---|---|
| `taxonomy.md` | Mappa cartelle → ruolo/contenuto. Fonte di verità per dove creare file. | prima di creare file | quando si aggiungono cartelle |
| `index.md` | Catalogo dei contenuti: file/note → di cosa trattano. Evita duplicati, fa trovare il file giusto senza scansionare tutto. | per orientarsi sui contenuti | a ogni file creato/rilevante modificato |
| `hot-cache.md` | Contesto caldo: aree toccate di recente, thread aperti, focus corrente. Letto **per primo** a inizio sessione per orientarsi in fretta. | a inizio sessione | a fine sessione |
| `log.md` | Registro cronologico append-only degli eventi significativi (decisioni, milestone, conflitti risolti). Leggibile da umano e AI. | quando serve la storia del *perché* | dopo ogni cambiamento significativo |

Tieni i file leggeri: `hot-cache.md` è una finestra mobile (sovrascrivi le voci vecchie), `log.md` è append-only ma sintetico, `index.md` una riga per voce.

Accanto ai quattro file di *stato* vivono i **companion** in `_meta/` (procedure +
script). L'AI legge `procedures.md` su richiesta; gli script girano via hook:

| File | Ruolo |
|---|---|
| `procedures.md` | Procedure operative dettagliate + formati dei file meta. Semi-statico: l'AI lo legge su richiesta, non a ogni turno. Serve a tenere CLAUDE.md compatto. |
| `sync.py` | Rigenera `index.md` e la sezione "File toccati" di `hot-cache.md`. Gira nello Stop hook. |
| `session-brief.sh` | Hook di **pre-turno**: a ogni messaggio inietta nel contesto il delta utente dall'ultimo commit `ai:` (vedi "Fase 3c"). Read-only, silenzioso se non c'è delta. |
| `check-claude-md.py` | Auditor deterministico anti-drift di CLAUDE.md (vedi sotto). |
| `check-frontmatter.py` | Auditor deterministico del frontmatter delle pagine: campi mancanti, valori fuori enum, tag non in taxonomy. Data-driven (legge lo schema da `taxonomy.md`). Warn-only, gira nel hook e a inizio sessione. |

### Perché un auditor deterministico per CLAUDE.md

La separazione regole/stato è il cuore della skill, ma resta una *buona
intenzione* finché qualcosa non la verifica: nel tempo CLAUDE.md tende ad
accumulare date, procedure intere e riferimenti a cartelle rinominate — è drift
reale, osservato sul campo. `check-claude-md.py` lo rende un controllo meccanico.
Segnala: (1) date/fatti datati → `log.md`; (2) procedure passo-passo →
`procedures.md`; (3) cataloghi/liste lunghe → `index.md`; (4) path inesistenti =
rename non propagati. Gira da solo a inizio sessione (`workspace-status.sh`) e nel
hook auto-commit quando CLAUDE.md cambia, così la regola «CLAUDE.md immutabile»
smette di dipendere dalla memoria dell'AI e diventa una proprietà osservabile del
vault.

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

---

## Fase 3b — Hook auto-commit (multi-agent)

Ogni agent ha la propria directory di configurazione (`.claude/`, `.agents/`,
`.gemini/`) con un proprio formato di hook. Il pattern è unico:

- **un solo script** in posizione neutrale: `hooks/auto-commit.sh` alla root
  del vault
- **ogni agent config** punta a quello stesso script
- aggiungere il supporto a un nuovo agent = creare il suo file di config
  puntando a `hooks/auto-commit.sh`

### Script canonico

Copia `vault-template/hooks/auto-commit.sh` in `hooks/auto-commit.sh`
nella root del vault, poi rendilo eseguibile:

```bash
chmod +x hooks/auto-commit.sh
```

Lo script (avvia `_meta/sync.py`, audit warn-only, pull, commit `ai:`, push) non
dipende dall'agent che lo invoca — è agnostico. Include una **guardia anti-loop**:
esce subito se è in corso un rebase/merge o se `HEAD` è detached, e abortisce il
`pull --rebase` se fallisce, così non lascia mai il repo in stato rotto (causa
tipica del ciclo detached-HEAD ↔ push fallito quando un altro processo — es.
Obsidian Git — sincronizza in parallelo).

### Config per agent

Copia i file dalla cartella `vault-template/` di questa skill:

```
vault-template/
├── CLAUDE.md.template        → CLAUDE.md            ← compila e rinomina (Fase 5)
├── hooks/
│   └── auto-commit.sh        → hooks/auto-commit.sh ← Stop hook (script unico)
├── _meta/
│   ├── sync.py               → _meta/sync.py
│   ├── session-brief.sh      → _meta/session-brief.sh   ← hook pre-turno (Fase 3c)
│   ├── check-claude-md.py    → _meta/check-claude-md.py
│   ├── check-frontmatter.py  → _meta/check-frontmatter.py
│   ├── procedures.md         → _meta/procedures.md
│   ├── taxonomy.md           → _meta/taxonomy.md    ← compila con le cartelle reali
│   ├── index.md              → _meta/index.md       ← starter (lo riempie sync.py)
│   ├── hot-cache.md          → _meta/hot-cache.md   ← starter
│   └── log.md                → _meta/log.md         ← starter
├── .claude/
│   └── settings.json         → .claude/settings.json
├── .agents/
│   └── settings.json         → .agents/settings.json
└── .gemini/
    └── settings.json         → .gemini/settings.json
```

Se il file di config di un agent esiste già, aggiungi solo il blocco hook
senza sovrascrivere le altre impostazioni.

**Formato hook per agent** — ogni agent usa la sua chiave e struttura.
I template in `vault-template/` riportano il formato corrente; se un agent
aggiorna la sua specifica, aggiorna il template corrispondente.
Per trovare il formato aggiornato: cerca nella documentazione ufficiale
dell'agent il termine `hooks` + `stop` o `afterTurn`.

| Agent | Config file | Chiave hook | Evento |
|---|---|---|---|
| Claude Code | `.claude/settings.json` | `hooks.Stop` | fine turno |
| Agents SDK | `.agents/settings.json` | `hooks.stop` | fine turno |
| Gemini CLI | `.gemini/settings.json` | `hooks.afterTurn` | fine turno |

Per aggiungere un agent non in lista: crea `.<agent>/settings.json` (o il
file di config che usa) con la chiave hook appropriata che invoca
`bash hooks/auto-commit.sh`. Poi aggiungi una riga alla tabella sopra.

### Cosa ottieni a fine ogni turno AI

| Operazione | Come |
|---|---|
| `_meta/index.md` ricostruito | `sync.py` scansiona tutti i .md del vault |
| `_meta/hot-cache.md` "File toccati" aggiornato | `sync.py` legge ultimi commit `ai:` |
| Audit anti-drift di CLAUDE.md (se modificato nel turno) | `check-claude-md.py`, warn-only |
| Audit frontmatter (se cambiano .md nel turno) | `check-frontmatter.py --fix`, warn-only + auto-registra tag ricorrenti |
| Modifiche committate con `ai:` | `auto-commit.sh` dopo sync |
| Push sul remote | `auto-commit.sh` |

**Cosa rimane all'AI:**
- `_meta/hot-cache.md` — "Focus corrente" e "Thread aperti"
- `_meta/log.md` — decisioni e milestone
- `_meta/taxonomy.md` — quando si crea una nuova cartella

---

## Fase 3c — Hook di pre-turno (delta utente)

Lo Stop hook (3b) chiude il turno committando `ai:`. Da solo è metà del ciclo:
quando l'utente lavora in Obsidian *tra* due turni AI, l'agente al messaggio
successivo non sa cosa è cambiato. `_meta/session-brief.sh` è la metà simmetrica.

- **Quando**: a ogni messaggio, prima che l'agente risponda (`UserPromptSubmit`
  per Claude Code; l'evento di pre-turno equivalente per gli altri agent).
- **Cosa fa**: stampa su stdout — che l'agente riceve in contesto — il
  **delta dall'ultimo commit `ai:`**: commit `vault:`, file non committati, risorse
  nuove in `_raw/`, righe con commenti `%%` nelle pagine cambiate. Tutto ciò che
  sta dopo l'ultimo `ai:` è, per costruzione, lavoro dell'utente.
- **Garanzie di progetto**: read-only (non tocca mai il repo, sicuro anche durante
  rebase/merge/detached); **silenzioso** quando non c'è delta (subito dopo un
  commit `ai:` il range è vuoto → zero rumore e zero token); output **cappato**
  (solo `--stat` ed estratti, mai diff interi); **non fallisce mai** (esce sempre
  0, così non blocca il prompt dell'utente).

L'agente usa il brief per *riconciliare* prima di agire: leggere cosa ha fatto
l'utente, evitare di sovrascriverlo, aggiornare lo stato vivo, processare `_raw/`
ed eseguire i `%%`. La procedura di risposta è in `_meta/procedures.md`
("Delta utente a inizio messaggio", "Commenti `%%`", "Inbox `_raw/`").

Cablaggio in `.claude/settings.json`:

```json
{ "hooks": { "UserPromptSubmit": [ { "hooks": [
  { "type": "command", "command": "bash _meta/session-brief.sh" } ] } ] } }
```

| Agent | Config file | Chiave hook pre-turno |
|---|---|---|
| Claude Code | `.claude/settings.json` | `hooks.UserPromptSubmit` (verificata) |
| Agents SDK | `.agents/settings.json` | `hooks.userPromptSubmit` (da confermare con la spec) |
| Gemini CLI | `.gemini/settings.json` | `hooks.beforeTurn` (da confermare con la spec) |

Lo script è agnostico: cambia solo la chiave dell'evento. Per gli agent diversi da
Claude Code verifica il nome dell'evento di pre-turno nella documentazione corrente
e aggiorna il template.

---

## Fase 4 — Struttura cartelle

```
vault/
├── CLAUDE.md          ← istruzioni immutabili (generato nel passo successivo)
├── .gitignore
├── hooks/
│   └── auto-commit.sh     ← Stop hook condiviso tra tutti gli agent
├── .claude/
│   └── settings.json      ← UserPromptSubmit → session-brief.sh · Stop → auto-commit.sh
├── .agents/
│   └── settings.json      ← pre-turno → session-brief.sh · stop → auto-commit.sh
├── .gemini/
│   └── settings.json      ← pre-turno → session-brief.sh · afterTurn → auto-commit.sh
├── _meta/             ← file di stato vivi, mantenuti dall'AI
│   ├── taxonomy.md         ← mappa cartelle → ruolo/contenuto
│   ├── index.md            ← catalogo dei contenuti (auto-rebuild da sync.py)
│   ├── hot-cache.md        ← contesto caldo (file toccati auto, focus manuale)
│   ├── log.md              ← registro eventi significativi (manuale)
│   ├── procedures.md       ← procedure operative + formati (companion, semi-statico)
│   ├── sync.py             ← aggiorna index e hot-cache (Stop hook)
│   ├── session-brief.sh    ← delta utente dall'ultimo ai: (pre-turno hook)
│   ├── check-claude-md.py  ← auditor anti-drift di CLAUDE.md (hook + sessione)
│   └── check-frontmatter.py ← auditor frontmatter pagine, data-driven (hook + sessione)
├── _raw/              ← inbox: risorse grezze da processare (esclusa da index)
├── daily-notes/       ← YYYY-MM-DD.md, una per giorno
├── <tema-1>/
├── <tema-2>/
└── ...
```

I quattro file di *stato* in `_meta/` sono descritti nella sezione "I file di
stato vivi"; `procedures.md`, `sync.py`, `session-brief.sh`, `check-claude-md.py`
e `check-frontmatter.py` sono i companion. Il CLAUDE.md non duplica il loro
contenuto: vi rimanda. Così resta immutabile mentre lo stato del vault evolve nei
file vivi.

---

## Fase 5 — Genera il CLAUDE.md e i file di stato

Genera il CLAUDE.md **e** i quattro file di stato `_meta/` insieme: il CLAUDE.md fa riferimento ai file vivi, quindi devono esistere fin dall'inizio (anche se inizialmente quasi vuoti). I companion `procedures.md`, `sync.py`, `session-brief.sh`, `check-claude-md.py` e `check-frontmatter.py` si copiano da `vault-template/` (Fase 3b). I template di stato e di CLAUDE.md sono anch'essi file in `vault-template/` (vedi tabella più sotto).

Compila il template con i dati reali del vault. Nessun placeholder non compilato: il file è caricato ad ogni sessione AI e deve essere immediatamente operativo.

Il CLAUDE.md va scritto **una volta sola**. Non contiene cataloghi, liste o stato che invecchiano — quelli vivono in `_meta/` e li aggiorna l'AI durante il lavoro. Se in futuro serve cambiare *le regole*, allora sì si tocca il CLAUDE.md; ma il flusso normale di lavoro non lo modifica mai.

Genera sempre **`CLAUDE.md`** come file canonico, indipendentemente dall'agent principale. Poi crea `AGENTS.md` e `GEMINI.md` come symlink che puntano a esso:

```bash
ln -sf CLAUDE.md AGENTS.md
ln -sf CLAUDE.md GEMINI.md
```

In questo modo i tre file sono sempre sincronizzati automaticamente: qualsiasi agent (Claude, Gemini, multi-agent) trova le istruzioni nel suo file, e c'è una sola fonte di verità da mantenere.

Per vault esistenti che hanno già `AGENTS.md` o `GEMINI.md` come file reali: controlla se il contenuto è equivalente a CLAUDE.md. Se sì, sostituisci con il symlink. Se no, unisci prima i contenuti, poi sostituisci.

Aggiungi i symlink al commit iniziale del vault (git li versiona correttamente come symlink, non come copie).

---

### I template sono file in `vault-template/`, non incollati qui

Per non duplicare (la regola d'oro della skill), i template **non sono ricopiati
in questo SKILL.md**: sono file reali sotto `vault-template/`, unica fonte di
verità. Si copiano nel vault e si compilano. Workflow:

| File | Origine | Cosa compilare dopo la copia |
|---|---|---|
| `CLAUDE.md` | `vault-template/CLAUDE.md.template` → rinomina in `CLAUDE.md` | nome vault, struttura, regole specifiche; togli le righe Skill non rilevanti |
| `_meta/taxonomy.md` | `vault-template/_meta/taxonomy.md` | cartelle reali dall'intervista + blocco `frontmatter-schema` |
| `_meta/index.md` | `vault-template/_meta/index.md` | nulla — lo riempie `sync.py` |
| `_meta/hot-cache.md` | `vault-template/_meta/hot-cache.md` | nulla — starter |
| `_meta/log.md` | `vault-template/_meta/log.md` | la data della voce `init` |
| `_meta/procedures.md` | `vault-template/_meta/procedures.md` | nulla — copia integrale; personalizza se serve |

Gli script (`sync.py`, `session-brief.sh`, `check-*.py`) e gli hook si copiano
come sono (Fase 3b). Dopo la copia, **compila `CLAUDE.md` con i dati reali del
vault**: nessun placeholder `[...]` o `<...>` deve restare, perché il file è
caricato ad ogni sessione AI e dev'essere operativo da subito.

`CLAUDE.md.template` già rispetta le proprie regole (niente date, niente liste
numerate ≥3, niente cataloghi): dopo averlo compilato, `check-claude-md.py` deve
passare pulito.

---

## Script di orientamento

Lo script `scripts/workspace-status.sh` (incluso in questa skill) esegue i comandi di orientamento in un colpo solo e può essere invocato dal CLAUDE.md:

```bash
bash <percorso-skill>/scripts/workspace-status.sh
```

Stampa: hot-cache, audit anti-drift di CLAUDE.md (`check-claude-md.py`), commit
recenti con legenda vault/ai, file modificati, modifiche non committate, daily
note di oggi. Funziona su vault con qualsiasi struttura di cartelle.

---

## Nota: pagina overview / home

Questa skill **non** genera una `overview.md`: la home funzionale del vault è
`_meta/hot-cache.md` (cosa sta succedendo) + `_meta/index.md` (cosa c'è). Se il
vault eredita una `overview.md` da `wiki-init`, tienila come **pagina di pura
navigazione che rimanda ai file vivi** — mai come catalogo di struttura duplicato,
che invecchia e contraddice `taxonomy.md`. `check-claude-md.py` audita solo
CLAUDE.md, quindi sta all'AI mantenere overview un semplice hub di link.
