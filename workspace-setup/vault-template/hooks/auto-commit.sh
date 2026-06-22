#!/usr/bin/env bash
# auto-commit.sh — Stop hook Claude Code / Antigravity.
# Chiamato alla fine di ogni turno AI.

set -euo pipefail

git rev-parse --git-dir &>/dev/null || exit 0

# 0. GUARDIA ANTI-LOOP. Non operare se il repo è in uno stato "speciale" o rotto:
#    un'altra operazione (Obsidian Git, o un rebase incagliato) è in corso, oppure
#    HEAD è scollegato. Committare/pushare qui peggiorerebbe il casino e può creare
#    il ciclo vizioso detached-HEAD ↔ push fallito. Meglio uscire pulito.
if [ -d "$(git rev-parse --git-path rebase-merge)" ] || \
   [ -d "$(git rev-parse --git-path rebase-apply)" ] || \
   [ -f "$(git rev-parse --git-path MERGE_HEAD)" ] || \
   [ -f "$(git rev-parse --git-path CHERRY_PICK_HEAD)" ]; then
    echo "auto-commit: operazione git in corso (rebase/merge) — salto questo turno." >&2
    exit 0
fi
if ! git symbolic-ref -q HEAD >/dev/null; then
    echo "auto-commit: HEAD scollegato (detached) — salto. Riattacca un branch prima." >&2
    exit 0
fi

# Trap errors and send a macOS notification
cleanup_on_error() {
  local exit_code=$?
  if [ $exit_code -ne 0 ]; then
    osascript -e "display notification \"Errore nel backup automatico del vault!\" with title \"AI Git Sync\" subtitle \"Codice errore: $exit_code\"" 2>/dev/null || true
  fi
}
trap cleanup_on_error EXIT

# 1. Aggiorna _meta/index.md e hot-cache "File toccati" prima di verificare
#    se ci sono modifiche — sync.py potrebbe produrre cambiamenti da committare.
if [ -f "_meta/sync.py" ]; then
    python3 _meta/sync.py 2>/dev/null || true
fi

# 1b. Audit anti-drift: gira SOLO se CLAUDE.md è cambiato in questo turno, così
#     segnala il drift nel momento in cui viene introdotto. Warn-only.
if [ -f "_meta/check-claude-md.py" ] && \
   git status --porcelain -- CLAUDE.md 2>/dev/null | grep -q .; then
    python3 _meta/check-claude-md.py || true
fi

# 1c. Audit frontmatter: gira SOLO se qualche .md è cambiato in questo turno.
#     --fix è SICURO: registra in taxonomy.md i soli tag ricorrenti non ancora
#     elencati (tiene la taxonomy sincronizzata). Tutto il resto (date/type/status
#     mancanti, valori fuori enum) è solo segnalato — richiede giudizio umano.
#     Warn-only: non blocca mai il commit.
if [ -f "_meta/check-frontmatter.py" ] && \
   git status --porcelain -- '*.md' 2>/dev/null | grep -q .; then
    python3 _meta/check-frontmatter.py --fix || true
fi

# 2. Esci se non ci sono modifiche (né da AI né da sync.py)
git diff --quiet && git diff --cached --quiet && exit 0

# 2b. Guardia esplicita ridondante: se per qualche motivo si arriva qui senza
#     modifiche reali da committare, esci comunque senza proseguire.
if [ -z "$(git status --porcelain)" ]; then
    exit 0
fi

# 3. Pull per incorporare auto-commit Obsidian Git degli ultimi minuti.
#    SICURO: se il rebase fallisce (es. conflitto su un merge commit), abortisce
#    subito così NON lascia mai un detached HEAD da cui il push fallirebbe.
if ! git pull --rebase --autostash 2>/dev/null; then
    git rebase --abort 2>/dev/null || true
    echo "auto-commit: pull --rebase fallito e abortito — committo locale, sync al prossimo giro." >&2
fi

# 4. Commit con prefisso ai:
git add -A
git commit -m "ai: auto-commit $(date +%Y-%m-%dT%H:%M)"

# 5. Push se c'è un remote e siamo (ancora) su un branch. Push semplice: se
#    fallisce perché siamo indietro, lascia che sia Obsidian Git a riconciliare
#    al prossimo ciclo invece di forzare un rebase qui.
if git remote get-url origin &>/dev/null && git symbolic-ref -q HEAD >/dev/null; then
    git push 2>/dev/null || echo "auto-commit: push rimandato (origin avanti?) — Obsidian Git riconcilierà." >&2
fi
