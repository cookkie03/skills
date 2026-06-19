---
name: wiki-artifact
description: >
  Creates visual and structured artifacts from wiki knowledge: canvas maps,
  Dataview/Bases queries, kanban boards, and task lists. Use when the user asks for
  something visual or structured: "crea uno schema", "fai una mappa", "visualizza le
  relazioni", "crea una board", "dammi una tabella dinamica", "organizza i task", "fai un kanban".
---

# Wiki Artifact

Genera artefatti visivi e strutturati dal wiki. I path reali si ricavano da
`_meta/taxonomy.md` (mai hardcodati); il file istruzioni locale del vault può fare override.

## Skill da usare

Le skill Obsidian sono di [kepano](https://github.com/kepano/obsidian-skills/tree/main/skills):

- `json-canvas` → file `.canvas`
- `obsidian-bases` → file `.base`
- `obsidian-markdown` → query inline e sintassi markdown

**Kanban**: nessuna skill kepano — gestione manuale (markdown + plugin Kanban; le
colonne sono heading `##`, i task checkbox sotto).

## Scegli l'artefatto

| Esigenza | Artifact | Skill | Dove salvare (ruolo in `taxonomy.md`) |
|---|---|---|---|
| Relazioni tra concetti/entità/pagine; schemi, mappe concettuali, flow | **Canvas** | `json-canvas` | `build` se attivo, altrimenti `artifact` |
| Vista dinamica su frontmatter; dashboard, tabelle, report di stato | **Dataview / .base** | `obsidian-bases`; inline → `obsidian-markdown` | inline → nella pagina rilevante; standalone → `operation` o `_meta/` |
| Task con stati multipli (work in progress) | **Kanban** | manuale (vedi sopra) | `operation` |
| Checklist semplice | **Task list** | — | task list del vault · `operation` · sezione in una pagina |

Se l'utente è indeciso, chiedi se vuole qualcosa **da guardare** (canvas) o **con cui
interagire** (kanban/base).

Per Kanban e Task list, raccogli i task dall'area operativa, dalle task list e dalle
pagine recenti rilevanti.

## Dopo ogni artifact

Appendi al log:

```markdown
## [YYYY-MM-DD] artifact | [tipo] | Titolo
- **File**: [[path/al/file]]
- **Based on**: [[pagine wiki consultate]]
```
