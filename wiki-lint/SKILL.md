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

Leggi `wiki/_meta/taxonomy.md` per i path attivi. Controlla prima gli invarianti comuni, poi le convenzioni del vault dichiarate nel file istruzioni locale.

---

## Prerequisiti

Leggi prima di iniziare:

1. `wiki/_meta/log.md	`
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

- File istruzioni agente mancante: verifica che esista almeno uno tra `CLAUDE.md`, `AGENTS.md`, `GEMINI.md` nella root del vault
- `taxonomy.md` mancante o incompleto: verifica che tutti i ruoli semantici siano dichiarati e che i path attivi esistano davvero nel vault
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

### Freshness & Deduplication

**Freshness via `updated:`:**

Per ogni source page con `raw_source_path` nel frontmatter:

- confronta il campo `updated:` della wiki page con il campo `updated:` del raw referenziato (se presente)
- se il raw ha `updated:` più recente → segnala come `ATTENZIONE: wiki page stale`
- se il raw non esiste più al path indicato ma non risulta archiviato → segnala come `ATTENZIONE: raw_source_path non risolvibile`

Per le wiki page in generale:

- se `updated:` è più di 90 giorni fa e la pagina ha wikilink in entrata attivi → `SUGGERIMENTO: verifica se il contenuto è ancora valido`
- se `updated:` è più di 90 giorni fa e la pagina non ha wikilink in entrata → `ATTENZIONE: pagina potenzialmente obsoleta e orfana`

**Deduplicazione:**

Individua candidati a merge o consolidamento:

- pagine con titoli molto simili (stesso termine root, varianti singolare/plurale, sinonimi evidenti)
- pagine con set di tag identici o quasi sovrapposti e contenuto simile per lunghezza e struttura
- concetti citati spesso via wikilink che hanno già una pagina molto simile esistente
- stub pages (< ~200 parole) che trattano lo stesso dominio di una pagina più grande già esistente

Classifica ogni candidato come:

- `MERGE`: contenuto quasi identico, una delle due è ridondante
- `CONSOLIDATE`: una è stub, l'altra è la pagina canonica dove andrebbe incorporata
- `REVIEW`: sovrapposizione parziale, decidere manualmente

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

## Freshness

- Wiki pages stale (raw aggiornato dopo): N → [[elenco]]
- Raw source_path non risolvibili: N → [[elenco]]
- Pagine non aggiornate da >90gg con link attivi: N
- Pagine non aggiornate da >90gg orfane: N

## Deduplication

| Pagina A | Pagina B | Tipo | Azione suggerita |
|----------|----------|------|-----------------|
| [[...]]  | [[...]]  | MERGE / CONSOLIDATE / REVIEW | ... |

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
