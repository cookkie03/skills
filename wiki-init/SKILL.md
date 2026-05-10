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

Parti da una base universale:

```text
vault-root/
├── AGENTS.md o CLAUDE.md
├── raw/
│   └── archived/
└── wiki/
    ├── _meta/
    │   ├── index.md
    │   ├── log.md
    │   ├── taxonomy.md
    │   └── hot-cache.md
    ├── overview.md
    ├── sources/
    ├── entities/
    ├── concepts/
    ├── syntheses/
    └── questions/
```

Poi aggiungi solo le aree davvero necessarie al profilo del vault, per esempio:

- `wiki/build/`
- `wiki/ops/`
- `wiki/decisions/`
- `wiki/lists/`
- `wiki/artifacts/`

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
- `wiki/_meta/taxonomy.md`
- `wiki/_meta/hot-cache.md`

### 2.4 `overview.md`

Genera una pagina overview leggera ma utile come punto di ingresso.

---

## Tipi di vault

I profili di vault servono soprattutto qui, in init.
Le altre skill devono poi restare profile-agnostic.

Profili tipici:

- software project
- business project
- research vault
- second brain
- hybrid vault

---

## Regola chiave

Il file istruzioni locale generato da `wiki-init` deve dichiarare sempre i mapping strutturali che evitano assunzioni hardcoded sbagliate nelle altre skill.
