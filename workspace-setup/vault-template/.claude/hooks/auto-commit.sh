#!/usr/bin/env bash
# auto-commit.sh — Stop hook Claude Code.
# Chiamato alla fine di ogni turno AI. Ordine operazioni:
#   1. sync _meta/ (index + hot-cache file toccati)
#   2. pull --rebase per incorporare auto-commit Obsidian Git recenti
#   3. commit con prefisso "ai:" e timestamp
#   4. push
# Esce silenziosamente se non ci sono modifiche da committare.

set -euo pipefail

git rev-parse --git-dir &>/dev/null || exit 0

# 1. Aggiorna _meta/index.md e hot-cache "File toccati" prima di verificare
#    se ci sono modifiche — sync.py potrebbe produrre cambiamenti da committare.
if [ -f "_meta/sync.py" ]; then
    python3 _meta/sync.py 2>/dev/null || true
fi

# 2. Esci se non ci sono modifiche (né da AI né da sync.py)
git diff --quiet && git diff --cached --quiet && exit 0

# 3. Pull per incorporare auto-commit Obsidian Git degli ultimi minuti
git pull --rebase --autostash 2>/dev/null || true

# 4. Commit con prefisso ai:
git add -A
git commit -m "ai: auto-commit $(date +%Y-%m-%dT%H:%M)"

# 5. Push se c'è un remote
git remote get-url origin &>/dev/null && git push || true
