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

Il file istruzioni locale del vault può dichiarare:

- cartelle equivalenti per ops, lists, build, artifacts
- tag canonici e frontmatter minimi
- policy su archivio raw e pending ingest

Il lint deve controllare prima gli invarianti comuni, poi le convenzioni specifiche del vault.

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
- pagine stale
- draft dimenticati
- tag non canonici
- frontmatter incompleto

(I conflitti tra pagine hanno una sezione dedicata sotto.)

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

**Freshness via mtime:**

Per ogni source page con `raw_source_path` nel frontmatter:

- confronta la data `updated:` della wiki page con il `mtime` del file raw referenziato
- se il raw è più recente della wiki page → segnala come `ATTENZIONE: wiki page stale`
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

## Conflitti e contraddizioni

I conflitti si individuano **per gruppi** di pagine correlate. L'agent non confronta ogni pagina con ogni altra: forma cluster di pagine collegate, poi cerca contraddizioni al loro interno.

### 1. Forma i cluster

Considera una pagina collegata a un'altra se vale almeno una di queste condizioni:

- wikilink diretto in entrata o in uscita
- riferimento reciproco nel frontmatter `related:`
- condivisione di 2+ tag
- menzione delle stesse entità (via wikilink) in entrambe
- stesso topic root nel titolo (es. "Authentication" e "Authentication patterns")
- stesso valore in un campo frontmatter discriminante (es. stesso `entity:` o stesso `decision_topic:`)

Per ogni cluster, esegui i controlli sotto.

### 2. Tipi di conflitto da cercare

| Tipo | Descrizione | Esempio |
|------|-------------|---------|
| `FACTUAL` | Stesso soggetto, proprietà mutuamente esclusive | "X fondato nel 2020" vs "X fondato nel 2019" |
| `STATUS` | Stessa entità / task / decisione con stato divergente nel frontmatter o nel corpo | `status: done` su pagina A, riferimento come pending su pagina B |
| `RECOMMENDATION` | Indicazioni opposte sulla stessa pratica | "usa sempre X" vs "evita X perché..." |
| `QUANTITATIVE` | Numeri o metriche diverse per la stessa quantità, senza contesto temporale | "5 utenti" vs "10 utenti" |
| `TEMPORAL` | Ordine logico violato (A dipende da B ma B è creato dopo A) | Decisione X richiama Y, ma Y ha `created:` posteriore |
| `PRESUPPOSITIONAL` | Pagine assumono baseline contrastanti | A presuppone monolite, B presuppone microservizi |
| `CATEGORICAL` | Stessa entità con tipo / categoria / tag divergenti | Pagina A dichiara entità come `tool`, B come `library` |

### 3. Segnali sintattici per estrarre i claim

Cerca nelle pagine del cluster:

- **copula**: "X è/sono Y", "X equivale a Y", "X corrisponde a Y"
- **modali**: "deve essere", "non può", "è obbligatorio", "vietato", "richiede"
- **polarità**: "supporta / non supporta", "compatibile / incompatibile", "attivo / disattivo"
- **numeri** associati a entità o metriche (versioni, conteggi, percentuali, importi)
- **date** associate a eventi (creazione, deprecazione, rilascio, scadenza)
- **campi frontmatter**: `status:`, `confidence:`, `type:`, `decision_status:`, `version:`

### 4. Procedura sistematica

Per ogni cluster:

1. **Estrai** i claim rilevanti da ogni pagina usando i segnali sopra
2. **Normalizza il soggetto** del claim usando i wikilink (riconosci sinonimi: `[[Auth]]` e `[[Authentication]]` puntano alla stessa entità)
3. **Raggruppa** i claim per soggetto + predicato
4. **Identifica conflitti diretti**: stesso soggetto + predicato con polarità o valore diverso
5. **Identifica conflitti indiretti**: claim A in pagina X implica logicamente la negazione di claim B in pagina Y

### 5. Quando NON segnalare

Non sono conflitti veri:

- Conflitti già risolti registrati nel `log.md`
- Pagine in stato `confidence: low` con claim esplicitamente speculativi o ipotetici
- Citazioni di opinioni di terze parti ("secondo X, A; secondo Z, B")
- Pagine che descrivono evoluzioni temporali esplicite ("prima era X, ora è Y", "fino alla v2 era X, dalla v3 è Y")
- Differenze di scope dichiarate (es. comportamento in ambiente A vs ambiente B)

### 6. Classificazione di gravità

- `CRITICO`: conflitto su pagine con `confidence: high`, o su fatti operativi attivi (decisioni applicate, configurazioni in uso, regole vincolanti)
- `ATTENZIONE`: conflitto tra pagine entrambe aggiornate di recente (< 90gg), nessuna chiaramente più autoritativa
- `SUGGERIMENTO`: conflitto in cui una pagina è chiaramente più recente o più autoritativa — proponi di allineare quella meno aggiornata

### 7. Azione suggerita per ogni conflitto

Quando segnali un conflitto, indica anche l'azione concreta:

- **Riconcilia**: una delle due è corretta — verifica con fonte primaria e aggiorna l'altra
- **Marca come domanda aperta**: nessuna delle due è chiaramente corretta — crea pagina nel ruolo `question`
- **Annota evoluzione temporale**: entrambe vere in momenti diversi — aggiungi contesto temporale alle pagine
- **Restringi lo scope**: entrambe vere in contesti diversi — chiarisci il dominio di applicabilità

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

- Wiki pages stale (raw più recente): N → [[elenco]]
- Raw source_path non risolvibili: N → [[elenco]]
- Pagine non aggiornate da >90gg con link attivi: N
- Pagine non aggiornate da >90gg orfane: N

## Deduplication

| Pagina A | Pagina B | Tipo | Azione suggerita |
|----------|----------|------|-----------------|
| [[...]]  | [[...]]  | MERGE / CONSOLIDATE / REVIEW | ... |

## Conflitti

| Tipo | Pagine coinvolte | Disaccordo (citato) | Azione suggerita |
|------|------------------|----------------------|------------------|
| FACTUAL / STATUS / RECOMMENDATION / QUANTITATIVE / TEMPORAL / PRESUPPOSITIONAL / CATEGORICAL | [[A]], [[B]], ... | "claim A" vs "claim B" | Riconcilia / Marca come domanda aperta / Annota evoluzione temporale / Restringi lo scope |

## Statistiche

- Pagine totali: N
- Pagine orfane: N
- Pending ingest: N
- Conflitti aperti: N (per tipo)
- Ultimo lint: YYYY-MM-DD
```

---

## Dopo il lint

1. Chiedi all'utente quali problemi risolvere subito.
2. Applica le fix richieste.
3. Registra il lint nel log.
4. Aggiorna `hot-cache.md`.
