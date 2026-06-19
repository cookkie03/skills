# Procedures

Procedure operative dettagliate. Lette su richiesta — non necessarie ad ogni sessione.

## File di stato vivi

| File | Ruolo | Aggiornato da |
|---|---|---|
| `taxonomy.md` | Mappa cartelle → contenuto | AI (manuale, quando si crea una cartella) |
| `index.md` | Catalogo contenuti del vault | sync.py (automatico a fine turno AI) |
| `hot-cache.md` | Contesto caldo: focus e thread aperti | AI (semantica) + sync.py (file toccati) |
| `log.md` | Storia del perché: decisioni, milestone | AI (manuale, append-only) |

## Come leggere il git log

- `vault: ...` → auto-commit Obsidian (utente ha lavorato in quell'intervallo di tempo)
- `ai: ...` → turno AI completato; la descrizione dice cosa è stato fatto
- File in `git status --short` → in modifica adesso, probabilmente aperti in Obsidian

## Durante la sessione

- Prima di leggere un file: `git pull` (incorpora auto-commit Obsidian degli ultimi minuti).
- Prima di committare manualmente: `git pull` per evitare conflitti con Obsidian Git.
- Se il pull genera conflitti: preferisci la versione con mtime più recente, salvo
  indicazioni diverse dell'utente.

## Mantenere CLAUDE.md immutabile

CLAUDE.md contiene solo regole stabili. Lo script `_meta/check-claude-md.py`
verifica meccanicamente che non accumuli contenuto che invecchia, e gira da solo
a inizio sessione (`workspace-status.sh`) e nel hook auto-commit quando CLAUDE.md
cambia. Se segnala qualcosa, sposta il contenuto nel file vivo giusto:

- **Date / fatti datati** → `_meta/log.md`
- **Procedure passo-passo** → `_meta/procedures.md` (in CLAUDE.md solo una riga di rimando)
- **Cataloghi / liste lunghe** → `_meta/index.md` o `taxonomy.md`
- **Path inesistenti** → rename non propagato: aggiorna i riferimenti

Esecuzione manuale: `python3 _meta/check-claude-md.py` (aggiungi `--strict` per
exit 1 sui problemi, utile in un pre-commit).

## Rinominare o spostare una cartella

Un rename non propagato lascia riferimenti rotti sparsi. Procedura:

1. `grep -rn "vecchio-nome" _meta/ CLAUDE.md` e aggiorna ogni riferimento.
2. Aggiorna `_meta/taxonomy.md` con la nuova struttura.
3. Registra il rename in `_meta/log.md` (tipo `refactor`) — **mai** in CLAUDE.md.
4. `python3 _meta/check-claude-md.py` per confermare che non resti nessun path rotto.

## File toccati di recente (NON editare a mano)

La sezione "File toccati di recente" in `hot-cache.md` la riscrive `sync.py` a ogni
turno (cappata alle ultime ~10 voci dai commit `ai:`). Qualsiasi modifica manuale
viene sovrascritta: non perderci tempo. Le sezioni "Focus corrente" e "Thread
aperti" sono invece tue — quelle aggiornale a mano.

## Formato `_meta/hot-cache.md`

Finestra mobile: sovrascrivi le voci superate, tienilo corto.

```markdown
# Hot Cache

**Aggiornato**: YYYY-MM-DD

## Focus corrente
- [su cosa si sta lavorando / dove si è arrivati]

## Thread aperti
- [ ] [cosa resta aperto per la prossima sessione]

## File toccati di recente
- [[...]]    ← auto-aggiornato da sync.py
```

## Formato `_meta/log.md`

Append-only. Una voce per evento significativo.

```markdown
## [YYYY-MM-DD] <tipo> | <titolo breve>
- [cosa è successo e perché, 1-2 righe]
```

Tipi: `decision` · `milestone` · `conflict-resolved` · `refactor` · `init`
