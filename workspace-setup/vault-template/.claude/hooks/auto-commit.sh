#!/usr/bin/env bash
# auto-commit.sh — committa le modifiche AI a fine turno Claude Code.
# Convenzione: "ai: ..." distinguibile dagli auto-commit "vault: ..." di Obsidian Git.
# Configurato da workspace-setup in .claude/settings.json (Stop hook).

set -euo pipefail

# Esci silenziosamente se non siamo in un repo git
git rev-parse --git-dir &>/dev/null || exit 0

# Esci se non ci sono modifiche da committare
git diff --quiet && git diff --cached --quiet && exit 0

# Pull prima di committare: incorpora gli auto-commit Obsidian Git recenti.
# --autostash: mette da parte le modifiche locali durante il pull, le ripristina dopo.
# || true: non bloccare se il pull fallisce (es. nessun remote ancora configurato).
git pull --rebase --autostash 2>/dev/null || true

# Commit con prefisso ai: e timestamp ISO
git add -A
git commit -m "ai: auto-commit $(date +%Y-%m-%dT%H:%M)"

# Push solo se c'è un remote configurato
git remote get-url origin &>/dev/null && git push || true
