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

1. **CLAUDE.md** — istruzioni operative, scritte una volta e **non più modificate**.È il file che l'AI carica ad ogni sessione: dice come lavorare, dove guardare, come committare.
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

Tieni i file leggeri: `hot-cache.md` è una finestra mobile (sovrascrivi le vocivecchie), `log.md` è append-only ma sintetico, `index.md` una riga per voce.

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

## Fase 3b — Hook Claude Code (auto-commit AI)

Claude Code supporta un hook `Stop` che scatta alla fine di ogni turno.
Con questo hook il vault si auto-committa dopo ogni risposta dell'AI, con prefisso `ai:` — senza che l'AI debba ricordarselo.

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

**`.claude/settings.json`** — se il file esiste già, aggiungi solo il blocco `Stop` dentro `hooks` senza sovrascrivere le altre impostazioni:

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

- `_meta/hot-cache.md` — sezioni "Focus corrente" e "Thread aperti": l'AI le aggiorna dopo ogni cambiamento di focus (vedi istruzioni nel CLAUDE.md)
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
Il CLAUDE.md non duplica il loro contenuto: vi rimanda. Così resta immutabile mentre lo stato del vault evolve nei file vivi.

---

## Fase 5 — Genera il CLAUDE.md e i file di stato

Genera il CLAUDE.md **e** i quattro file `_meta/` insieme: il CLAUDE.md fa riferimento ai file vivi, quindi devono esistere fin dall'inizio (anche se inizialmente quasi vuoti).

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

### Template CLAUDE.md

Questo file si scrive **una volta sola** e non si tocca nel flusso normale.
Contiene solo quello che serve ad ogni messaggio: struttura, convenzioni, comandi di orientamento, regole. Le procedure dettagliate e i formati dei file meta vivono in `_meta/procedures.md` — l'AI le legge su richiesta, non le carica ogni turno.

````markdown
# [Nome Vault]

[1-2 righe: scopo, contenuto principale, lingua di lavoro.]

## Struttura

```
<cartella-1>/    # [cosa contiene]
<cartella-2>/    # [cosa contiene]
daily-notes/     # YYYY-MM-DD.md
_meta/           # taxonomy · index · hot-cache · log · procedures · sync.py
```

Mappa estesa in `_meta/taxonomy.md`. Procedure operative in `_meta/procedures.md`.

## Convenzione commit

| Prefisso | Autore |
|---|---|
| `vault: {{date}}` | Obsidian Git — utente |
| `ai: <descrizione>` | AI (questa sessione) |

Usa sempre `ai:` — mai `vault:`.

## A inizio sessione

```bash
git pull
cat _meta/hot-cache.md
git log --oneline -15
git status --short
cat daily-notes/$(date +%Y-%m-%d).md
```

Sintetizza: dov'eravamo (hot-cache) · cosa è cambiato (log ai: vs vault:) · task aperti. 
`_meta/index.md` solo se cerchi un file specifico. Procedure in `_meta/procedures.md`.

## A fine sessione

- Aggiorna `_meta/hot-cache.md`: Focus corrente + Thread aperti (formato in procedures.md).
- Se evento significativo: appendi a `_meta/log.md` (formato in procedures.md).
- Se nuova cartella: aggiorna `_meta/taxonomy.md`.
- Index, commit e push: automatici via Stop hook.

## Regole operative

- Prima di creare file: leggi `_meta/taxonomy.md`.
- Non creare cartelle senza accordo esplicito.
- File in `git status` = in uso dall'utente — non toccare senza chiedere.
- Preferisci modificare file esistenti.
- [Regole specifiche di questo vault]

## Skill

| Operazione | Skill |
|---|---|
| Preprocessing audio, immagini, Office | `wiki-preprocess` |
| Crawling URL | `crawl4ai` |
| Sintassi Obsidian | `obsidian-markdown` |
| File .base / .canvas | `obsidian-bases` · `json-canvas` |
| Artefatti visivi | `wiki-artifact` |
| Health check | `wiki-lint` |

[Rimuovi le righe non rilevanti per questo vault.]
````

---

## Template `_meta/taxonomy.md`

Genera questo file insieme al CLAUDE.md. È la fonte di verità estesa per la struttura del vault — il CLAUDE.md la richiama, l'AI la legge prima di creare file in cartelle non ovvie.

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

Compila con le cartelle reali emerse dall'intervista. Aggiorna quando si aggiungono cartelle nuove.

---

## Template `_meta/procedures.md`

Contiene tutto quello che è stato tolto dal CLAUDE.md per tenerlo compatto.
L'AI la legge su richiesta — non viene caricata ad ogni sessione.

```markdown
# Procedures

## File di stato vivi

| File | Ruolo | Aggiornato da |
|---|---|---|
| `taxonomy.md` | Mappa cartelle → contenuto | AI (manuale) |
| `index.md` | Catalogo contenuti del vault | sync.py (auto) |
| `hot-cache.md` | Contesto caldo: focus e thread aperti | AI (parte semantica) + sync.py (file toccati) |
| `log.md` | Storia del perché: decisioni, milestone | AI (manuale, append-only) |

## Come leggere il git log

- `vault: ...` → auto-commit Obsidian (utente ha lavorato in quell'intervallo)
- `ai: ...` → turno AI completato; la descrizione dice cosa è stato fatto
- File in `git status --short` → in modifica adesso — non toccare senza chiedere

## Durante la sessione

- Prima di leggere un file: `git pull` (incorpora auto-commit Obsidian recenti).
- Prima di committare manualmente: `git pull` per evitare conflitti.
- Se il pull genera conflitti: preferisci la versione con mtime più recente.

## Formato `_meta/hot-cache.md`

Finestra mobile: sovrascrivi le voci superate, tienilo corto.

~~~markdown
# Hot Cache

**Aggiornato**: YYYY-MM-DD

## Focus corrente
- [su cosa si sta lavorando / dove si è arrivati]

## Thread aperti
- [ ] [cosa resta aperto per la prossima sessione]

## File toccati di recente
- [[...]]    ← auto-aggiornato da sync.py
~~~

## Formato `_meta/log.md`

Append-only. Una voce per evento significativo.

~~~markdown
## [YYYY-MM-DD] <tipo> | <titolo breve>
- [cosa è successo e perché, 1-2 righe]
~~~

Tipi: `decision` · `milestone` · `conflict-resolved` · `refactor` · `init`
```

---

## Template `_meta/index.md`

Catalogo dei contenuti. A setup è quasi vuoto; cresce man mano che il vault si popola. Una riga per voce, raggruppata per cartella.

```markdown
# Index

Catalogo dei contenuti del vault. Aggiornato dall'AI a ogni file rilevante creato o modificato. Una riga per voce.

## <tema-1>/
- [[<tema-1>/nota-esempio]] — di cosa tratta in una riga

## <tema-2>/
-
```

---

## Template `_meta/hot-cache.md`

Contesto caldo: finestra mobile su dove si sta lavorando. Sovrascrivibile, sempre corto.

```markdown
# Hot Cache

Contesto di lavoro recente. Finestra mobile: le voci vecchie si sovrascrivono. Letto a inizio sessione per riprendere il filo.

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

Registro cronologico degli eventi significativi del vault (decisioni, milestone, conflitti risolti). Append-only, sintetico.

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

Lo script `scripts/workspace-status.sh` (incluso in questa skill) esegue i comandi di orientamento in un colpo solo e può essere invocato dal CLAUDE.md:

```bash
bash <percorso-skill>/scripts/workspace-status.sh
```

Stampa: commit recenti con legenda vault/ai, file toccati, modifiche non committate, daily note di oggi. Funziona su vault con qualsiasi strutturadi cartelle.
