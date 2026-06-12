---
name: workspace-context
description: >
  Orienta l'AI all'inizio di una sessione di lavoro su un vault Obsidian workspace.
  Usa questa skill per definire come l'AI si orienta: legge git log, distingue
  commit utente da commit AI, legge la daily note di oggi.
  Nei vault ben configurati, la procedura di orientamento è già nel CLAUDE.md —
  questa skill documenta il razionale e i dettagli di interpretazione.
---

# Workspace Context

Documenta come l'AI si orienta all'inizio di ogni sessione su un vault workspace.

Nei vault creati con `vault-setup`, la procedura concreta (comandi da eseguire)
è direttamente nel `CLAUDE.md` del vault, dove l'AI la trova automaticamente
ad ogni sessione. Questa skill spiega il razionale e i dettagli di
interpretazione — utile per configurare vault nuovi o per aggiornare CLAUDE.md
di vault esistenti.

---

## Procedura di orientamento

Dalla root del vault:

```bash
git log --oneline -20          # commit recenti
git diff HEAD~3 --stat         # file toccati
git status --short             # modifiche non committate
cat daily-notes/$(date +%Y-%m-%d).md   # daily note di oggi
```

Oppure usa lo script incluso:

```bash
bash <path-skill>/scripts/workspace-status.sh
```

---

## Distinguere commit utente da commit AI

Il vault usa una convenzione esplicita nei messaggi di commit:

| Prefisso | Autore | Significato |
|---|---|---|
| `vault: 2025-06-12T10:30:00` | Obsidian Git | Auto-commit dell'utente che lavora in Obsidian |
| `ai: <descrizione>` | AI (Claude Code) | Modifiche fatte dall'AI in una sessione precedente |
| `init: ...` | Setup manuale | Commit di inizializzazione vault |

Nel `git log` si legge immediatamente chi ha fatto cosa:

```
a1b2c3d vault: 2025-06-12T10:42:15        ← utente ha lavorato qui
e4f5g6h ai: aggiorna riepilogo progetto X  ← AI sessione precedente
i7j8k9l vault: 2025-06-12T09:18:03        ← utente
m1n2o3p vault: 2025-06-11T22:05:44        ← utente ieri sera
```

L'AI deve sempre committare con `ai: <descrizione>` — mai con `vault:`.

---

## Interpretare git log + git status

**Commit `vault:` ravvicinati** → l'utente ha lavorato attivamente.
Guarda quali file sono toccati con `git diff <hash-1> <hash-2> --stat`.

**Commit `ai:` recenti** → l'AI aveva già operato. Guarda la descrizione
per capire cosa è stato fatto e evitare duplicati.

**File in `git status --short`** → modifiche non ancora committate.
Sono il lavoro più recente dell'utente (Obsidian Git committa ogni 10 min,
quindi al massimo 10 minuti di lavoro non committato). Indica che l'utente
è probabilmente in questa area adesso.

**Assenza di commit nelle ultime ore** → Obsidian Git potrebbe non essere
attivo, o l'utente non ha lavorato nel vault. Non assumere nulla: chiedi.

---

## Interpretare la daily note

La daily note è il contesto dichiarato dall'utente. Cerca:

- Cosa sta lavorando oggi (menzione esplicita di file, progetti, task)
- Task aperti (`- [ ]`) → cose in sospeso
- Sezioni tipo "In corso", "Focus", "TODO" se il template le prevede

Se la daily note non esiste per oggi: chiedi all'utente su cosa vuole lavorare
prima di procedere.

---

## Aggiornare CLAUDE.md di vault esistenti

Se un vault esistente non ha la procedura di orientamento nel CLAUDE.md,
aggiungila (vedi template in `vault-setup`). La procedura deve stare nel
CLAUDE.md per essere eseguita automaticamente ad ogni sessione — non richiede
che l'utente dica esplicitamente "orientati".

---

## Script workspace-status.sh

Lo script in `scripts/workspace-status.sh` esegue i comandi sopra in sequenza.
Gestisce vault con meno di 3 commit e cerca la daily note nei path più comuni:
`daily-notes/`, `Daily Notes/`, `Journal/`, `Diario/`, root.

```bash
bash <path-skill>/scripts/workspace-status.sh
```
