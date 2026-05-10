---
name: wiki-lint
description: >
  Health-checks an LLM Wiki vault, finding structural problems, stale content,
  contradictions, and maintenance gaps. Use when the user says: "lint", "health check",
  "com'è messo il wiki?", "controlla la wiki", "trova problemi", "cosa è da aggiornare".
---

# Wiki Lint

Health check del wiki. Produce un report strutturato con priorità e azioni concrete.

---

## Contratto comune

Questa skill deve funzionare in qualunque profilo di vault dopo l'init.

Non assumere che ogni vault abbia:

- `daily-notes/`
- `wiki/lists/`
- la stessa struttura interna

Il file istruzioni locale del vault può dichiarare:

- cartelle equivalenti per ops, lists, build, artifacts
- uso o non uso di daily notes
- tag canonici e frontmatter minimi
- policy su archivio raw e pending ingest

Il lint deve controllare prima gli invarianti comuni, poi le convenzioni specifiche del vault.

---

## Prerequisiti

Leggi prima di iniziare:

1. `wiki/_meta/log.md`
2. `wiki/_meta/index.md`
3. `wiki/_meta/taxonomy.md`
4. `wiki/_meta/hot-cache.md`

---

## Checklist

Classifica ogni problema come:

- `CRITICO`
- `ATTENZIONE`
- `SUGGERIMENTO`

### Struttura e navigabilità

- pagine orfane
- wikilink rotti
- `index.md` incompleto
- `overview.md` non aggiornato rispetto ai cambiamenti importanti

### Contenuto e qualità

- concetti spesso citati ma senza pagina
- claims in conflitto
- pagine stale
- draft dimenticati
- tag non canonici
- frontmatter incompleto

### Sources e inbox

- pending ingest nelle inbox dichiarate dal vault
- raw sources già ingestiti ma non archiviati
- source pages con `raw_source_path` non più risolvibile

### Operatività

- liste non riviste, se il vault usa liste
- task stagnanti o bloccati nell'area operativa del vault

### Session management

- `hot-cache.md` datato
- log incompleto rispetto ai file aggiornati

---

## Report output

```markdown
# Wiki Lint Report — [YYYY-MM-DD]

## CRITICO
- [problema] -> [azione concreta]

## ATTENZIONE
- [problema] -> [azione concreta]

## SUGGERIMENTO
- [problema] -> [azione concreta]

## Statistiche
- Pagine totali: N
- Pagine orfane: N
- Pending ingest: N
- Ultimo lint: YYYY-MM-DD
```

---

## Dopo il lint

1. Chiedi all'utente quali problemi risolvere subito.
2. Applica le fix richieste.
3. Registra il lint nel log.
4. Aggiorna `hot-cache.md`.
