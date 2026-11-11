#!/usr/bin/env bash
# workspace-status.sh — stato del vault per l'orientamento AI a inizio sessione.
# Eseguire dalla root del vault.
# Convenzione: "vault: ..." = Obsidian Git (utente) | "ai: ..." = AI

set -euo pipefail

echo "=== Hot cache (contesto caldo: dove eravamo) ==="
if [ -f "_meta/hot-cache.md" ]; then
    cat "_meta/hot-cache.md"
else
    echo "(nessun _meta/hot-cache.md)"
fi

echo ""
echo "=== Audit anti-drift CLAUDE.md ==="
if [ -f "_meta/check-claude-md.py" ]; then
    python3 _meta/check-claude-md.py || true
else
    echo "(nessun _meta/check-claude-md.py — vedi vault-template/_meta/)"
fi

echo ""
echo "=== Audit frontmatter delle pagine ==="
if [ -f "_meta/check-frontmatter.py" ]; then
    python3 _meta/check-frontmatter.py || true
else
    echo "(nessun _meta/check-frontmatter.py — vedi vault-template/_meta/)"
fi

echo ""
echo "=== Commit recenti (ultimi 15) ==="
echo "  vault: ... = utente (Obsidian Git)   |   ai: ... = AI (sessioni precedenti)"
echo ""
git log --oneline -15

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
    echo ""
    echo "⚠️  questi file sono in modifica attiva — non editarli senza chiedere"
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
fi
