---
name: wiki-init
description: >
  Initializes a new LLM Wiki vault for any project type. Use when the user wants to
  create a new wiki from scratch: "inizializza la wiki", "crea un nuovo vault",
  "setup wiki per il progetto X", "voglio creare una wiki per Y", "nuovo vault Obsidian".
---

# Wiki Init

Crea un nuovo vault LLM Wiki per qualsiasi tipo di progetto.

Questa è la skill che differenzia davvero i profili di vault.
Le altre skill wiki devono poi restare trasversali e utili in tutti i contesti.

Il processo è in due fasi: **intervista** -> **generazione**.

---

## Obiettivo del bootstrap

`wiki-init` deve produrre:

- struttura iniziale del vault
- file istruzioni locale (`AGENTS.md` o `CLAUDE.md`)
- `_meta/` bootstrap
- overview iniziale
- contratto locale che le altre skill possano seguire senza ambiguità

Il contratto locale deve dichiarare sempre:

- cartelle reali
- tipi pagina canonici
- aree opzionali come `lists`, `ops`, `build`, `decisions`, `artifacts`
- mapping locali come `raw/papers` vs `raw/pdfs`

---

## Fase 1 — Intervista

Poni le domande in modo conversazionale.

### Blocco A — Identità del vault

1. Cosa traccia questo vault?
2. Che tipo di vault è?
   - progetto software
   - progetto business
   - ricerca
   - secondo cervello
   - ibrido
3. Lavori da solo o con collaboratori?

### Blocco B — Contenuto e flusso

4. Che materiale finirà in `raw/`?
5. Ci sono aree già chiare o vuoi partire minimale?

### Blocco C — Operatività

7. Qual è l'agent principale?
8. Che output ti aspetti dal wiki?
9. Vuoi tracciare decisioni nel tempo?

### Blocco D — Dettagli opzionali

10. Ci sono domini tecnici specifici?
11. Devi condividere il wiki con altri?
12. Preferenze linguistiche?
13. Livello di complessità desiderato?

---

## Fase 2 — Generazione

### 2.1 Struttura cartelle

La struttura non è universale: dipende dal profilo del vault emerso nell'intervista.

La base invariante è sempre:

```text
vault-root/
├── AGENTS.md o CLAUDE.md
├── raw/
│   └── archived/
└── wiki/
    ├── _meta/
    │   ├── index.md
    │   ├── log.md
    │   ├── taxonomy.md   ← fonte di verità per tutte le skill wiki-*
    │   └── hot-cache.md
    └── overview.md
```

Le sottocartelle di `wiki/` sono determinate dal profilo. Vedi la sezione **Tipi di vault** per le strutture per profilo.

Usa nomi di cartelle che riflettono il dominio del vault: per un vault di ricerca ha senso `papers/` e `findings/`, non `sources/` e `syntheses/`. Per un second brain ha senso `people/` e `ideas/`, non `entities/` e `syntheses/`.

Includi solo le aree che il vault usa davvero. Non generare cartelle vuote di riserva.

### 2.2 File istruzioni locale

Genera `AGENTS.md` o `CLAUDE.md` in base al sistema usato dal vault.

Deve contenere:

1. identità del vault
2. struttura cartelle
3. regole fondamentali
4. frontmatter standard
5. query operative
6. skill rilevanti
7. override locali che le altre skill devono rispettare

Non includere lì dentro le procedure operative complete delle skill.

### 2.3 `_meta/` iniziali

Genera:

- `wiki/_meta/index.md`
- `wiki/_meta/log.md`
- `wiki/_meta/hot-cache.md`
- `wiki/_meta/taxonomy.md` ← il più importante: tutte le skill lo leggono per risolvere i path

`taxonomy.md` deve seguire questo formato esatto:

````markdown
---
vault_type: software-project | research | second-brain | business | hybrid
vault_name: ""
language: it | en
---

# Taxonomy

## Ruoli semantici → Path

I ruoli semantici sono fissi. I path sono specifici di questo vault.
Le skill wiki-* non usano mai path hardcodati: leggono sempre questa tabella.

| Ruolo       | Path              | Attivo |
|-------------|-------------------|--------|
| `source`    | `wiki/<path>/`    | sì/no  |
| `knowledge` | `wiki/<path>/`    | sì/no  |
| `entity`    | `wiki/<path>/`    | sì/no  |
| `synthesis` | `wiki/<path>/`    | sì/no  |
| `decision`  | `wiki/<path>/`    | sì/no  |
| `question`  | `wiki/<path>/`    | sì/no  |
| `operation` | `wiki/<path>/`    | sì/no  |
| `list`      | `wiki/<path>/`    | sì/no  |
| `artifact`  | `wiki/<path>/`    | sì/no  |
| `build`     | `wiki/<path>/`    | sì/no  |

## Cartelle raw → Path

| Tipo      | Path              |
|-----------|-------------------|
| default   | `raw/`            |
| audio     | `raw/audio/`      |
| documents | `raw/...`         |
| archived  | `raw/archived/`   |

## Page types canonici

I valori ammessi per `type:` nel frontmatter di questo vault:
`source`, `knowledge`, `entity`, `synthesis`, `decision`, `question`
````

Compila la tabella dei ruoli in base al profilo scelto. Dichiara tutti i ruoli anche quelli con `Attivo: no`, così le skill non devono inferire l'assenza.

### 2.4 `overview.md`

Genera una pagina overview leggera ma utile come punto di ingresso.

---

## Tipi di vault

I profili determinano le sottocartelle di `wiki/` e i path da compilare in `taxonomy.md`.
Le altre skill restano profile-agnostic leggendo la taxonomy.

### software-project

```text
wiki/
├── sources/       # ruolo source    (doc lette, RFC, articoli tecnici)
├── components/    # ruolo entity    (moduli, servizi, librerie, API)
├── concepts/      # ruolo knowledge (pattern, pratiche, tecnologie)
├── architecture/  # ruolo synthesis (analisi, decisioni architetturali)
├── decisions/     # ruolo decision
├── questions/     # ruolo question
├── ops/           # ruolo operation (task, sprint, bug tracking)
└── artifacts/     # ruolo artifact
```

Opzionale: `wiki/build/` (ruolo `build`) per documentazione di build e deploy.

### research

```text
wiki/
├── papers/        # ruolo source    (articoli letti, dataset, esperimenti)
├── subjects/      # ruolo entity    (autori, strumenti, aree tematiche)
├── theories/      # ruolo knowledge (teorie, modelli, framework)
├── findings/      # ruolo synthesis (risultati, conclusioni, ipotesi)
├── decisions/     # ruolo decision
└── questions/     # ruolo question
```

Opzionale: `wiki/ops/` (ruolo `operation`) se la ricerca ha un flusso operativo attivo.

### second-brain

```text
wiki/
├── sources/       # ruolo source    (libri, podcast, articoli)
├── people/        # ruolo entity    (persone, community, autori)
├── notes/         # ruolo knowledge (appunti, conoscenza)
├── ideas/         # ruolo synthesis (connessioni, sintesi personali)
├── decisions/     # ruolo decision
├── questions/     # ruolo question
├── lists/         # ruolo list      (reading list, watchlist, raccolte)
└── ops/           # ruolo operation
```

### business-project

```text
wiki/
├── sources/       # ruolo source    (documenti, meeting notes, research)
├── stakeholders/  # ruolo entity    (clienti, partner, team)
├── processes/     # ruolo knowledge (processi, metodologie, guide)
├── strategies/    # ruolo synthesis (strategie, analisi, report)
├── decisions/     # ruolo decision
├── questions/     # ruolo question
├── ops/           # ruolo operation
└── artifacts/     # ruolo artifact
```

Opzionale: `wiki/lists/` (ruolo `list`).

### hybrid

Struttura personalizzata basata sull'intervista. Scegli nomi di cartella che rispecchiano il dominio specifico. Usa i ruoli semantici come guida concettuale, non come nomi obbligatori.

---

## Regola chiave

Il file istruzioni locale generato da `wiki-init` deve dichiarare sempre i mapping strutturali che evitano assunzioni hardcoded sbagliate nelle altre skill.
