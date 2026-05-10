---
name: wiki-artifact
description: >
  Creates visual and structured artifacts from wiki knowledge: canvas maps, Dataview
  queries, kanban boards, and task lists. Use when the user asks for something visual
  or structured: "crea uno schema", "fai una mappa", "visualizza le relazioni",
  "crea una board", "dammi una tabella dinamica", "organizza i task", "fai un kanban".
---

# Wiki Artifact

Genera artefatti visivi e strutturati dal wiki.

---

## Contratto comune

Questa skill deve funzionare in vault diversi senza assumere che esistano sempre gli stessi folder.

Il file istruzioni locale del vault può ridefinire:

- dove salvare artifact visuali
- dove vive l'area operativa
- se esistono liste, board, dashboard o build docs

Usa come default `wiki/artifacts/`, `wiki/ops/` e l'area più vicina al contenuto, ma lascia prevalere i path locali dichiarati dal vault.

---

## Scegli l'artefatto giusto

| Esigenza | Artifact |
|---------|----------|
| Relazioni tra concetti, entità o pagine | Canvas |
| Task con stati | Kanban |
| Vista dinamica su frontmatter | Dataview o `.base` |
| Checklist semplice | Task list markdown |

Se l'utente è indeciso, chiedi se vuole qualcosa da guardare o qualcosa con cui interagire.

---

## Canvas

Usa per:

- schemi architetturali
- mappe concettuali
- graph di relazioni
- diagrammi di flusso

Usa sempre `json-canvas`.

Salvataggio:

- architettura / sistema -> area build o artifacts del vault
- mappa concettuale -> syntheses/artifacts del vault
- overview visiva -> posizione dichiarata dal vault per artifact top-level

---

## Dataview e Bases

Usa per:

- dashboard
- tabelle dinamiche
- liste filtrate
- report sullo stato delle pagine

Usa `obsidian-bases` per `.base`.
Per query inline in markdown, usa `obsidian-markdown`.

Salvataggio:

- query inline -> nella pagina rilevante
- dashboard standalone -> `_meta/`, `ops/` o area equivalente del vault

---

## Kanban

Usa per work in progress con stati multipli.

Salvataggio:

- area operativa del vault
- default: `wiki/ops/kanban-<nome>.md`

Raccogli i task dall'area operativa, dalle task list e dalle pagine recenti rilevanti.

---

## Task list

Usa per checklist semplici.

Salvataggio:

- task list del vault
- area operativa
- sezione in una pagina rilevante

---

## Dopo ogni artifact

Appendi al log:

```markdown
## [YYYY-MM-DD] artifact | [tipo] | Titolo
- **File**: [[path/al/file]]
- **Based on**: [[pagine wiki consultate]]
```
