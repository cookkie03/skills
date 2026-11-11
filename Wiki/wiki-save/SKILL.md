---
name: wiki-save
description: >
  Saves a query response, insight, or elaborated analysis as a permanent wiki page.
  Use when the user says: "salva questa risposta", "aggiungi al wiki", "memorizza questo",
  "crea una pagina su questo", "salva l'analisi", "voglio tenermi questa sintesi".
---
# Wiki Save

Trasforma una risposta elaborata in una pagina wiki permanente.

---

Leggi `_meta/taxonomy.md` per i path. Il file istruzioni locale può ridefinire tipi frontmatter canonici e policy locali — prevale sempre sul comportamento default.

---

## Quando salvare

Salva se la risposta è:

- una sintesi cross-source
- un'analisi non ovvia
- una decisione con motivazione
- un framework o checklist riutilizzabile
- un insight che merita memoria durevole

Non salvare se è solo:

- una risposta fattuale semplice già presente nel wiki
- un briefing volatile
- un output destinato a un altro sistema

---

## Procedura

### 1. Determina il tipo di pagina

Leggi `_meta/taxonomy.md` e ricava il path reale per il ruolo semantico corretto prima di creare o aggiornare la pagina.

| Tipo risposta                 | Ruolo semantico | `type`      |
| ----------------------------- | --------------- | ----------- |
| Analisi / comparazione        | `synthesis`     | `synthesis` |
| Framework / guida             | `knowledge`     | `knowledge` |
| Decisione                     | `decision`      | `decision`  |
| Risposta su entità specifica  | `entity`        | `entity`    |

Il path effettivo (`findings/`, `architecture/`, `notes/`, ecc.) è dichiarato nella taxonomy del vault, non in questa skill.

### 2. Crea o aggiorna la pagina

Frontmatter base suggerito:

```yaml
---
title: ""
type: synthesis | knowledge | decision | entity
tags: []
sources:
  - "[[sources/slug1]]"
created: YYYY-MM-DD
updated: YYYY-MM-DD
confidence: medium
status: reviewed
related: []
---
```

Per decisioni, aggiungi il campo locale appropriato, di default `decision_status`.

### 3. Collega la pagina al wiki

- aggiungi wikilink dalle pagine che ne beneficiano
- aggiorna `_meta/index.md`
- aggiorna `overview.md` solo se cambia davvero la mappa del vault

### 4. Log e hot cache

Appendi al log:

```markdown
## [YYYY-MM-DD] save | Titolo pagina
- **Type**: synthesis / concept / decision
- **Sources consulted**: [[sources/slug1]], [[concepts/slug2]]
- **New page**: [[syntheses/slug]]
```

Aggiorna `hot-cache.md` con la nuova pagina tra le pagine toccate.

---

## Decisioni

Una decisione può nascere da:

- una query
- una discussione di lavoro
- un ingest precedente
- una riflessione esplicita dell'utente

Formato minimo consigliato:

```markdown
## Contesto

## Opzioni valutate

## Decisione

## Motivazione

## Conseguenze
```
