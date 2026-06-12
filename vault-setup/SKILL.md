---
name: vault-setup
description: >
  Configura un vault Obsidian come workspace collaborativo con tracking git.
  Usa questa skill per creare un nuovo vault workspace o allineare un vault
  esistente: "crea un vault", "inizializza workspace", "aggiungi git al vault",
  "configura Obsidian Git", "setup vault per lavorare con l'AI".
  Distinto da wiki-init: questo paradigma non separa wiki/ e raw/, usa cartelle
  tematiche flat e git come fonte di verità per le modifiche.
---

# Vault Setup

Configura un vault Obsidian come workspace collaborativo dove utente e AI
lavorano insieme sui file, con git come fonte di verità per il tracking
delle modifiche nel tempo.

---

## Differenza con wiki-init

`wiki-init` crea vault con struttura wiki (`wiki/` + `raw/`) ottimizzata per
l'ingest di materiale grezzo e la generazione di pagine strutturate.

`vault-setup` crea vault **workspace**: cartelle tematiche flat, nessuna
distinzione wiki/raw, git come strumento operativo quotidiano.

Scegli `vault-setup` quando il vault è uno spazio di lavoro attivo (note,
documenti, progetti in evoluzione) piuttosto che una knowledge base da consultare.

---

## Prerequisiti

- Git installato (`git --version`)
- Obsidian con il plugin **Obsidian Git** installato
  (Settings → Community Plugins → cerca "Obsidian Git" → Install → Enable)
- Account su GitHub o Gitea con accesso SSH configurato

---

## Struttura raccomandata

```
vault/
├── CLAUDE.md | AGENTS.md      ← istruzioni per l'AI (vedi sotto)
├── .gitignore
├── _meta/
│   └── taxonomy.md             ← mappa cartelle: fonte di verità per l'AI
├── daily-notes/                ← una nota per giorno (YYYY-MM-DD.md)
├── <tema-1>/                   ← cartelle tematiche (definite con l'utente)
├── <tema-2>/
└── ...
```

Nessuna cartella `raw/` o `wiki/`. Le cartelle tematiche dipendono dal dominio
del vault e vengono stabilite durante l'intervista iniziale con l'utente.

---

## Setup nuovo vault

### 1. Crea la cartella e inizializza git

```bash
mkdir nome-vault && cd nome-vault
git init
```

### 2. Crea `.gitignore`

```gitignore
# Obsidian — workspace state (non versionare)
.obsidian/workspace.json
.obsidian/workspace-mobile.json
.obsidian/cache

# Trash e temp
.trash/
*.tmp

# OS
.DS_Store
Thumbs.db
```

Le impostazioni plugin (`.obsidian/plugins/`) e i temi rimangono versionati.

### 3. Struttura iniziale

```bash
mkdir -p _meta daily-notes
```

Crea `_meta/taxonomy.md` (vedi sezione dedicata).

### 4. Crea il remote

**GitHub:**
```bash
# Con GitHub CLI:
gh repo create nome-vault --private --source=. --remote=origin --push
# Oppure manualmente:
git remote add origin git@github.com:<user>/nome-vault.git
```

**Gitea:**
```bash
# Crea il repo dall'interfaccia web di Gitea, poi:
git remote add origin git@<gitea-host>:<user>/nome-vault.git
```

### 5. Primo commit e push

```bash
git add .
git commit -m "init: vault setup"
git push -u origin main
```

### 6. Configura Obsidian Git

In Obsidian → Settings → Obsidian Git:

| Impostazione | Valore consigliato |
|---|---|
| Vault backup interval (min) | `10` |
| Auto pull on startup | ✅ abilitato |
| Push on backup | ✅ abilitato |
| Pull updates on startup | ✅ abilitato |
| Commit message | `vault: {{date}}` |

Con questi valori il vault si sincronizza automaticamente ogni 10 minuti
e all'avvio. Su mobile, se la batteria è un vincolo, usa `0` come intervallo
e affidati al commit manuale (pulsante nella ribbon).

---

## Allineamento vault esistente

Se il vault non è ancora su git:

```bash
cd /path/to/vault
git init
# crea .gitignore come sopra
git add .
git commit -m "init: existing vault"
```

Se manca il remote:
```bash
# crea il repo su GitHub/Gitea, poi:
git remote add origin <url>
git push -u origin main
```

Se manca solo la configurazione del plugin: segui il punto 6 sopra.

Se il vault ha già `wiki/` e `raw/` (paradigma wiki-init):
Non è necessario migrare. I due paradigmi coesistono. Aggiungi il git
setup e usa `workspace-context` per l'orientamento AI mantenendo la struttura
esistente.

---

## `_meta/taxonomy.md`

Questo file è la fonte di verità per l'AI: dice dove creare nuovi file
e cosa contiene ogni cartella.

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
```

Compilalo con le cartelle reali del vault. L'AI legge questo file prima di
creare qualsiasi file nuovo.

---

## File istruzioni per l'AI

Genera il file in base all'agente principale usato nel vault:

- `CLAUDE.md` per Claude / Claude Code
- `AGENTS.md` per setup multi-agent o agenti non specificati
- `GEMINI.md` per Gemini

**Template:**

```markdown
# [Nome Vault]

[1-2 righe: cosa contiene, chi lo usa.]

## Struttura

Vault workspace con cartelle tematiche flat (no wiki/raw).
Mappa completa in `_meta/taxonomy.md`.

```
<cartella-1>/    # [contenuto]
<cartella-2>/    # [contenuto]
daily-notes/     # note giornaliere YYYY-MM-DD.md
_meta/           # taxonomy e metadati
```

## Orientamento a inizio sessione

Usa la skill `workspace-context` per leggere git log + daily note di oggi
prima di iniziare a lavorare.

## Regole operative

- Prima di creare nuovi file, leggi `_meta/taxonomy.md` per scegliere la cartella.
- Non creare cartelle nuove senza accordo con l'utente.
- Preferisci modificare file esistenti piuttosto che crearne di nuovi.

## Skill disponibili

| Operazione | Skill |
|---|---|
| Orientamento a inizio sessione | `workspace-context` |
| Preprocessing audio/immagini/Office | `wiki-preprocess` |
| Crawling URL | `crawl4ai` |
```

---

## Intervista iniziale (per vault nuovi)

Prima di generare la struttura, poni queste domande:

1. Per cosa verrà usato il vault? (progetto, area di lavoro, dominio)
2. Che tipo di file ci metti? (note, documenti, codice, riferimenti, ...)
3. Hai già in mente dei nomi per le aree tematiche?
4. Usi GitHub o Gitea come remote?
5. Quale agent principale? (Claude, Gemini, altro)

Proponi la struttura cartelle basandoti sulle risposte, poi chiedi conferma
prima di generare i file.
