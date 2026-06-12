---
name: workspace-context
description: >
  Orienta l'AI all'inizio di una sessione di lavoro su un vault Obsidian workspace.
  Usa questa skill per capire cosa l'utente ha fatto di recente, su cosa sta
  lavorando oggi, e quali file richiedono attenzione — senza che l'utente debba
  spiegarlo da zero ogni volta.
  Attivala all'inizio di ogni sessione o quando l'utente dice "dove eravamo",
  "cosa ho fatto ieri", "fammi un punto della situazione".
---

# Workspace Context

Legge lo stato del vault per orientarsi prima di lavorare, usando git come
fonte di verità per le modifiche recenti e la daily note come contesto
dichiarato dall'utente.

---

## Orientamento a inizio sessione

Lancia lo script incluso dalla directory radice del vault:

```bash
bash <path-skill>/scripts/workspace-status.sh
```

Lo script stampa in sequenza:
1. Ultimi 20 commit (cosa è cambiato e quando)
2. File modificati negli ultimi 3 commit (con conteggio righe)
3. Modifiche non ancora committate
4. Contenuto della daily note di oggi

Se lo script non è raggiungibile, esegui manualmente:

```bash
# Commit recenti
git log --oneline -20

# File toccati negli ultimi 3 commit
git diff HEAD~3 --stat

# Modifiche non committate
git status --short

# Daily note di oggi
cat daily-notes/$(date +%Y-%m-%d).md
```

---

## Cosa fare con l'output

Dopo aver letto git log + daily note:

**Dai commit** estrai:
- File modificati di recente → candidati per continuare il lavoro
- Pattern di attività (es. "ieri ha toccato molto X e poco Y")
- Eventuali commit message informativi lasciati dall'utente

**Dalla daily note** estrai:
- Su cosa l'utente sta lavorando oggi / ha lavorato ieri
- Task aperti (`- [ ]`) → cosa è in sospeso
- Menzione di file specifici → focus dichiarato

**Dalle modifiche non committate** (git status):
- File in lavorazione attiva in questo momento

---

## Dove creare nuovi file

Prima di creare qualsiasi file, leggi `_meta/taxonomy.md` per capire
la struttura delle cartelle tematiche del vault.

Non creare cartelle nuove senza accordo esplicito con l'utente.

---

## Segnali da comunicare all'utente

Se rilevi queste situazioni, comunicale prima di procedere:

- Modifiche non committate su molti file → possibile lavoro non salvato
- Nessun commit nelle ultime ore in un vault con auto-commit a 10 min →
  Obsidian Git potrebbe non essere attivo
- Daily note mancante per oggi → chiedere all'utente su cosa vuole lavorare

---

## Note operative

- Non modificare file senza richiesta esplicita o accordo nella sessione.
- Obsidian Git auto-committa ogni ~10 min: `git log` riflette il lavoro
  recente con buona granularità, ma un gap non è necessariamente un problema.
- Se il vault usa il paradigma wiki (ha `wiki/` e `raw/`), questo script
  funziona ugualmente: git log non dipende dalla struttura del vault.
