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
- file istruzioni locale (`CLAUDE.md`, `AGENTS.md` o `GEMINI.md`)
- `_meta/` bootstrap
- overview iniziale

Il file istruzioni locale deve dichiarare sempre:

- cartelle reali e loro ruolo semantico
- tipi pagina canonici
- mapping locali come `raw/papers` vs `raw/pdfs`

---

## Fase 1 — Intervista

Poni le domande in modo conversazionale.

### Blocco A — Identità e scopo

1. Per cosa verrà usato questo vault? Qual è il suo scopo principale?
2. Chi lo usa? Lavori da solo o con collaboratori?

### Blocco B — Contenuto e vocabolario

3. Cosa pensi di metterci dentro? Che tipo di materiale elaborerai?
4. Come chiami il materiale grezzo che elabori? (es. articoli, paper, appunti, clip, documenti, note...)
5. Come chiami le cose che vuoi ricordare e consultare nel tempo?
6. Ci sono termini tecnici o di settore che usi regolarmente nel tuo dominio?
7. Ci sono aree già chiare o vuoi partire minimale?

### Blocco C — Operatività

8. Qual è l'agent principale? (Claude, Gemini, altro — determina quale file istruzioni generare)
9. Che output ti aspetti dal wiki?
10. Vuoi tracciare decisioni nel tempo?

### Blocco D — Dettagli opzionali

10. Ci sono domini tecnici specifici?
11. Devi condividere il wiki con altri?
12. Preferenze linguistiche?
13. Livello di complessità desiderato?

### Proposta collaborativa

Dopo aver raccolto le risposte, **prima di generare**:

1. Proponi i nomi di cartella derivati dal vocabolario dell'utente. Usa i default dove il vocabolario non suggerisce nomi più precisi.
2. Spiega brevemente il ragionamento dietro le scelte non ovvie (es. "ho usato `papers/` invece di `sources/` perché hai detto che lavori solo con articoli accademici").
3. Chiedi conferma o modifica prima di procedere alla generazione.

---

## Fase 2 — Generazione

### 2.1 Struttura cartelle

La base invariante è sempre:

```text
vault-root/
├── CLAUDE.md | AGENTS.md | GEMINI.md
├── raw/
│   └── archived/
└── wiki/
    ├── _meta/
    │   ├── index.md
    │   ├── log.md
    │   ├── taxonomy.md   ← fonte di verità per tutte le skill wiki-*
    │   └── hot-cache.md
    ├── overview.md
    ├── sources/       # ruolo source    — default, rinominabile
    ├── entities/      # ruolo entity    — default, rinominabile
    ├── concepts/      # ruolo knowledge — default, rinominabile
    ├── syntheses/     # ruolo synthesis — default, rinominabile
    └── questions/     # ruolo question  — default, rinominabile
```

I nomi delle sottocartelle mostrati sopra sono **default validi per la maggior parte dei vault**. Si rinominano solo quando il dominio ha un vocabolario più preciso e riconoscibile — vedi la sezione **Principi guida** per sapere quando e come.

Aree aggiuntive si aggiungono solo se il vault le usa davvero. Per l'area operativa, vedi i **Principi guida** sulla consolidazione di `ops/`, `decisions/` e `build/`.

### 2.2 File istruzioni locale

Genera il file in base al sistema dell'agente principale dichiarato nell'intervista:

- `CLAUDE.md` per ambienti Claude / Claude Code
- `GEMINI.md` per ambienti Gemini
- `AGENTS.md` per setup multi-agent o sistemi non specificati (default neutro)

Il file deve essere abbastanza conciso da stare in contesto all'inizio di ogni sessione senza sprecare token. Non includere le procedure operative complete delle skill.

**Template:**

````markdown
# [Nome Vault]

[1-2 righe su cosa traccia questo vault e chi lo usa.]

## Struttura

```
wiki/
├── [cartella]/    # [ruolo semantico] — [cosa contiene]
├── ...
```

Per il mapping completo ruoli → path, vedi `wiki/_meta/taxonomy.md`.

## Regole operative

- Mai saltare informazioni: ogni dato nel source deve trovare posto nel wiki
- Mai fare riassunti riduttivi: preserva la grana del dato
- Se il source più recente contraddice una pagina esistente, il source vince (salvo `confidence: high`)

## Skill

| Operazione                  | Skill           |
|-----------------------------|-----------------|
| Ingest / aggiornamento      | `wiki-ingest`   |
| Query / briefing            | `wiki-query`    |
| Salva risposta elaborata    | `wiki-save`     |
| Artifact visivi             | `wiki-artifact` |
| Health check                | `wiki-lint`     |
| Preprocessing audio/img     | `wiki-preprocess` |

## Override locali

[Eventuali regole specifiche di questo vault che sovrascrivono il comportamento default delle skill.]
````

### 2.3 `_meta/` iniziali

Genera:

- `wiki/_meta/index.md`
- `wiki/_meta/log.md`
- `wiki/_meta/hot-cache.md`
- `wiki/_meta/taxonomy.md` ← il più importante: tutte le skill lo leggono per risolvere i path

`taxonomy.md` deve seguire questo formato esatto:

````markdown
---
vault_name: ""
language: it | en
---

# Taxonomy

## Ruoli semantici → Path

I ruoli semantici sono fissi. I path sono specifici di questo vault.
Le skill wiki-* non usano mai path hardcodati: leggono sempre questa tabella.

| Ruolo       | Path           | Attivo |
|-------------|----------------|--------|
| `source`    | `wiki/<path>/` | sì/no  |
| `knowledge` | `wiki/<path>/` | sì/no  |
| `entity`    | `wiki/<path>/` | sì/no  |
| `synthesis` | `wiki/<path>/` | sì/no  |
| `question`  | `wiki/<path>/` | sì/no  |
| `operation` | `wiki/<path>/` | sì/no  |
| `list`      | `wiki/<path>/` | sì/no  |
| `artifact`  | `wiki/<path>/` | sì/no  |

Nota: `decision` e `build` non sono ruoli-cartella separati per default. Le pagine di tipo `decision` vivono nel path `operation`. Se il vault ha volumi che giustificano cartelle dedicate, aggiungile con i loro ruoli qui.

## Cartelle raw → Path

| Tipo      | Path            |
|-----------|-----------------|
| default   | `raw/`          |
| audio     | `raw/audio/`    |
| documents | `raw/`          |
| archived  | `raw/archived/` |

## Page types canonici

I valori ammessi per `type:` nel frontmatter di questo vault:
`source`, `knowledge`, `entity`, `synthesis`, `decision`, `question`
````

Compila la tabella con i path reali emersi dall'intervista. Dichiara tutti i ruoli, anche quelli con `Attivo: no`, così le skill non devono inferire l'assenza.

### 2.4 `overview.md`

Genera una pagina overview leggera ma utile come punto di ingresso.

---

## Principi guida per la scelta delle cartelle

I nomi default (`sources/`, `entities/`, `concepts/`, `syntheses/`, `questions/`) sono validi per la maggior parte dei vault. Usa questi principi per decidere quando tenerli e quando rinominarli.

**Usa i default quando:**
- Il dominio è generico o ibrido e non impone un lessico specifico
- L'utente non ha espresso preferenze di naming durante l'intervista
- Rinominare aggiungerebbe confusione invece di chiarezza

**Rinomina quando:**
- Esiste un termine di dominio più preciso e immediatamente riconoscibile (es. `papers/` invece di `sources/` per chi lavora solo con articoli accademici; `people/` invece di `entities/` per un vault centrato sulle relazioni)
- Il nome default risulta ambiguo nel contesto specifico

**Come derivare i nomi:**
Usa il vocabolario emerso nell'intervista — è il segnale più forte. Se l'utente ha detto "i miei paper" e "le mie annotazioni", quei termini sono candidati migliori dei default.

**Stabilità nel tempo:**
Preferisci nomi che non diventino obsoleti al cambiare del progetto. Nomi astratti (`entities/`, `concepts/`) reggono meglio di nomi troppo specifici (`microservices/`, `sprints/`).

**Minimalismo:**
Non creare cartelle per ruoli che il vault non usa ancora. Si aggiungono quando servono, non per anticipazione.

**Consolidazione dell'area operativa:**
Per la maggior parte dei vault, un'unica cartella `ops/` (ruolo `operation`) è sufficiente per task, decisioni e build docs. Crea `decisions/` o `build/` come cartelle separate solo se i volumi o i workflow sono chiaramente distinti. Le pagine di tipo `decision` possono vivere in `ops/` con `type: decision` nel frontmatter.
