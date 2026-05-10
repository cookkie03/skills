---
name: wiki-query
description: >
  Queries the LLM Wiki to answer questions, retrieve information, and generate on-demand
  outputs from accumulated knowledge. Use when the user asks anything about the vault's
  domain: "dimmi tutto su X", "confronta A e B", "cosa so di Y", "riassumi Z",
  "dammi un briefing", "cosa c'è da fare?", "stato del progetto", "trova informazioni su".
---
# Wiki Query

Risponde a domande usando come fonte primaria la conoscenza accumulata nel wiki.

---

## Contratto comune

Assumi che il file istruzioni locale del vault sia già nel contesto e possa dichiarare:

- area operativa primaria
- sezione domande aperte
- cartelle equivalenti per sources, build, lists, artifacts
- policy su briefing e pending ingest

Usa le categorie logiche del vault prima dei path specifici.

---

## Prerequisiti

Leggi sempre prima di rispondere:

1. `wiki/_meta/hot-cache.md`
2. `wiki/_meta/index.md`
3. le pagine rilevanti e i loro wikilink pertinenti

---

## Procedura standard

1. Identifica le pagine rilevanti dall'`index.md`.
2. Leggi le pagine trovate e segui i wikilink davvero utili.
3. Rispondi citando esplicitamente le pagine wiki.
4. Se la risposta ha valore durevole, proponi `wiki-save`.

Se il wiki non basta, dillo esplicitamente e proponi il passo successivo:

- cercare nei raw sources
- fare autoresearch
- registrare una domanda aperta

---

## Output disponibili

| Formato             | Quando            | Skill                 |
| ------------------- | ----------------- | --------------------- |
| Markdown page       | Risposta standard | `obsidian-markdown` |
| Tabella comparativa | Confronti         | `obsidian-markdown` |
| Lista               | Liste             | `wiki-artifact`     |
| Kanban              | Task              | `wiki-artifact`     |
| Canvas `.canvas`  | Mappa visiva      | `json-canvas`       |
| Vista `.base`     | Dati strutturati  | `obsidian-bases`    |

---

## Briefing di sessione

**Trigger**: "briefing", "cosa c'è da fare?", "fammi il punto", apertura del vault.

Leggi in sequenza:

1. `wiki/_meta/hot-cache.md`
2. `wiki/overview.md`
3. area operativa primaria del vault
4. sezione delle domande aperte
5. pending ingest dichiarati dal vault

Produce:

```markdown
## Briefing [YYYY-MM-DD]

**Stato**: [1 riga sullo stato corrente]

**Da fare**:
- [ ] ...

**Domande aperte**:
- ...

**Pending ingest**:
- ...

**Suggerimento sessione**: [cosa conviene fare ora]
```

Il briefing non va salvato nel wiki se è puramente volatile.

---

## Autoresearch

Se la domanda richiede informazioni non presenti nel wiki e l'agent ha accesso al web:

1. fai la ricerca
2. salva il risultato in `raw/`
3. esegui ingest con `wiki-ingest`
4. rispondi dal wiki aggiornato

Segnala sempre quando una risposta include conoscenza arrivata dal web.

---

## Domande aperte

Se la domanda rivela un gap nel wiki, crea o aggiorna una pagina nell'area `questions` o nell'equivalente dichiarato dal vault, con lo stato coerente con le convenzioni locali.
