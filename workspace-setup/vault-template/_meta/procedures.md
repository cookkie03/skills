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
