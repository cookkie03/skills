#!/usr/bin/env bash
# workspace-status.sh — stato del vault per l'orientamento dell'AI a inizio sessione.
# Eseguire dalla directory radice del vault.
# Convenzione commit: "vault: ..." = utente (Obsidian Git), "ai: ..." = AI.

set -euo pipefail

echo "=== Commit recenti (ultimi 20) ==="
echo "  vault: ... → Obsidian Git (utente)   |   ai: ... → AI sessioni precedenti"
echo ""
git log --oneline -20

echo ""
echo "=== File modificati (ultimi 3 commit) ==="
if git rev-parse HEAD~3 &>/dev/null; then
    git diff HEAD~3 --stat
else
    git diff --stat HEAD 2>/dev/null || echo "(meno di 3 commit nel vault)"
fi

echo ""
echo "=== Modifiche non committate (lavoro in corso) ==="
STATUS=$(git status --short)
if [ -n "$STATUS" ]; then
    echo "$STATUS"
else
    echo "(nessuna)"
fi

echo ""
echo "=== Daily note di oggi ==="
TODAY=$(date +%Y-%m-%d)
FOUND=""
for path in \
    "daily-notes/$TODAY.md" \
    "Daily Notes/$TODAY.md" \
    "Journal/$TODAY.md" \
    "Diario/$TODAY.md" \
    "$TODAY.md"; do
    if [ -f "$path" ]; then
        FOUND="$path"
        break
    fi
done

if [ -n "$FOUND" ]; then
    echo "($FOUND)"
    echo ""
    cat "$FOUND"
else
    echo "(nessuna daily note per oggi: $TODAY)"
    echo "Percorsi cercati: daily-notes/, Daily Notes/, Journal/, Diario/, root"
fi
