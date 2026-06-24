#!/usr/bin/env bash
# session-brief.sh — delta utente dall'ultimo commit "ai:".
#
# Gira a OGNI messaggio come hook di inizio turno
# (Claude Code: UserPromptSubmit; altri agent: l'evento equivalente di pre-turno).
# Stampa su stdout un brief COMPATTO di tutto ciò che l'utente ha cambiato da
# quando l'AI ha lavorato l'ultima volta, così l'agent è consapevole del delta e
# può riconciliare (index/taxonomy/log), processare l'inbox _raw/ ed eseguire i
# commenti %% lasciati dentro le pagine.
#
# Principi di progetto:
#   - SILENZIOSO quando non c'è delta: output vuoto = niente in contesto, costo ~0.
#     (Subito dopo un commit "ai:" il range è vuoto → naturale idempotenza.)
#   - READ-ONLY: non tocca MAI il repo. Sicuro anche durante rebase/merge/detached.
#   - BOUNDED: niente diff interi, solo --stat + estratti cappati, per non gonfiare
#     il contesto a ogni messaggio.
#   - NON FALLISCE MAI: esce sempre 0. Un hook di pre-turno che fallisce bloccherebbe
#     il prompt dell'utente; qui qualsiasi errore è degradato a "brief parziale".
#
# Convenzione commit: "ai: ..." = AI | "vault: ..." / altro = utente.

# Volutamente NIENTE `set -e`/`pipefail`: con molte pipe verso `head`, SIGPIPE
# farebbe abortire lo script a metà. `set -u` resta utile per gli unset.
set -u
trap 'exit 0' EXIT   # garanzia: qualunque cosa accada, l'hook esce pulito.

# ── tetti di output (proteggono il budget di contesto) ──────────────────────────
MAX_COMMITS=15
MAX_RAW=30
MAX_COMMENTS=30
MAX_COMMENT_FILE_SCAN=200   # non grepare i %% su più di N file cambiati
COMMENT_LINE_MAXLEN=160

git rev-parse --git-dir >/dev/null 2>&1 || exit 0

# Ultimo commit "ai:" sul branch corrente. Vuoto su un vault dove l'AI non ha
# ancora lavorato. `--grep` filtra il messaggio; `^ai:` evita falsi positivi
# (es. una nota che cita "ai:" nel corpo non è un soggetto).
last_ai="$(git log -n1 --grep='^ai:' --format='%H' 2>/dev/null)"

# ── insiemi di file cambiati ────────────────────────────────────────────────────
# committed_files: file toccati dai commit utente dopo l'ultimo "ai:".
#   (Essendo last_ai il PIÙ RECENTE commit ai:, dopo di esso ci sono solo commit
#    utente: il range last_ai..HEAD è esattamente "cosa ha fatto l'utente".)
if [ -n "$last_ai" ]; then
    committed_files="$(git diff --name-only "$last_ai"..HEAD 2>/dev/null)"
else
    committed_files=""
fi

# worktree_files: modifiche non ancora committate (file aperti ora in Obsidian).
#   -uall espande le cartelle non tracciate ai singoli file (così una risorsa nuova
#   in _raw/ compare come _raw/<file>, non come "_raw/" collassato).
#   --porcelain è stabile; tolgo i 3 char di stato; per i rename tengo il "-> nuovo".
worktree_files="$(git status --porcelain -uall 2>/dev/null | sed -e 's/^...//' -e 's/^.* -> //')"

changed_all="$(printf '%s\n%s\n' "$committed_files" "$worktree_files" | sed '/^$/d' | sort -u)"

# ── accumulo del brief (stampato solo se non vuoto) ─────────────────────────────
brief=""
add()     { brief+="$1"$'\n'; }
section() { [ -n "$1" ] && { add ""; add "$2"; add "$1"; }; }

# 1. Stato di partenza
if [ -z "$last_ai" ]; then
    recent="$(git log -n5 --format='  %h %s (%cr)' 2>/dev/null)"
    [ -n "$recent" ] && section "$recent" \
        "ℹ️  Nessun commit ai: ancora: primo turno AI su questo vault. Commit recenti:"
fi

# 2. Commit dell'utente dall'ultimo ai:
if [ -n "$last_ai" ]; then
    user_commits="$(git log "$last_ai"..HEAD --format='  %h %s (%cr)' 2>/dev/null | head -n "$MAX_COMMITS")"
    section "$user_commits" "📥 Commit dell'utente dall'ultimo turno AI:"

    diffstat="$(git diff --stat "$last_ai"..HEAD 2>/dev/null | head -n 41)"
    section "$diffstat" "📊 File cambiati nei commit utente (last ai:..HEAD):"
fi

# 3. Lavoro non committato (file probabilmente aperti ORA in Obsidian)
wip="$(git status --short 2>/dev/null | head -n 41)"
section "$wip" "✏️  Modifiche non committate (in uso adesso — non editarle senza chiedere):"

# 4. Inbox: risorse nuove o cambiate in qualunque _raw/
raw_changed="$(printf '%s\n' "$changed_all" | grep -E '(^|/)_raw/' | head -n "$MAX_RAW")"
section "$raw_changed" "📦 Inbox _raw/ (da processare → wiki-preprocess / wiki-ingest):"

# 5. Commenti %% nelle pagine cambiate (istruzioni inline utente→AI)
scan_files="$(printf '%s\n' "$changed_all" | grep -E '\.md$' | head -n "$MAX_COMMENT_FILE_SCAN")"
comments=""
ccount=0
while IFS= read -r f; do
    [ -n "$f" ] && [ -f "$f" ] || continue
    while IFS= read -r match; do
        [ -n "$match" ] || continue
        if [ "$ccount" -ge "$MAX_COMMENTS" ]; then
            comments+="  … (altri commenti %% non mostrati)"$'\n'
            break 2
        fi
        # tronca righe lunghe per non sforare il contesto
        if [ "${#match}" -gt "$COMMENT_LINE_MAXLEN" ]; then
            match="${match:0:$COMMENT_LINE_MAXLEN}…"
        fi
        comments+="  $f:$match"$'\n'
        ccount=$((ccount + 1))
    done < <(grep -nE '%%' -- "$f" 2>/dev/null)
done < <(printf '%s\n' "$scan_files")
section "${comments%$'\n'}" "💬 Commenti %% nelle pagine cambiate (istruzioni utente da eseguire e poi risolvere):"

# ── output ──────────────────────────────────────────────────────────────────────
if [ -n "$brief" ]; then
    printf '%s\n' "=== DELTA UTENTE dall'ultimo commit ai: ==="
    printf '%s' "$brief"
    printf '%s\n' "" \
        "→ Riconcilia ciò che è cambiato: aggiorna _meta/index·taxonomy·log se serve," \
        "  processa l'inbox _raw/, esegui e poi rimuovi/risolvi i commenti %%."
fi
exit 0
