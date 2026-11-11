#!/usr/bin/env python3
"""
check-claude-md.py — auditor deterministico anti-drift per CLAUDE.md.

CLAUDE.md deve contenere SOLO regole stabili (struttura, convenzioni, comandi di
orientamento, regole operative). Tutto ciò che invecchia va nei file vivi. Questo
script lo verifica meccanicamente, così la regola «CLAUDE.md immutabile» smette di
essere solo una buona intenzione e diventa una proprietà osservabile del vault.

Cosa segnala:
  1. Fatti datati (date YYYY-MM-DD)        → vanno in _meta/log.md
  2. Procedure passo-passo (liste numerate) → vanno in _meta/procedures.md
  3. Cataloghi (lunghe liste di [[wikilink]]) → vanno in _meta/index.md
  4. Riferimenti a path inesistenti         → rename non propagati (drift)

Il check 4 è il più prezioso: cattura le rinomine di cartelle non propagate
(es. `master/` → `career/`) confrontando i path citati con il filesystem reale.

Uso:
  python3 _meta/check-claude-md.py            # warn-only, exit 0 (default, sicuro per hook)
  python3 _meta/check-claude-md.py --strict   # exit 1 se trova problemi (per CI / pre-commit)
  python3 _meta/check-claude-md.py --file PATH # audita un file diverso da CLAUDE.md

Pensato per girare:
  - a inizio sessione (workspace-status.sh) → audita il drift accumulato
  - nel Stop hook quando CLAUDE.md è cambiato → segnala il drift appena introdotto
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

ROOT = Path.cwd()

# Cartelle da non indicizzare quando si verifica l'esistenza dei path.
PRUNE_DIRS = {".git", ".obsidian", "node_modules", "__pycache__", ".trash"}

DATE_RE = re.compile(r"\b20\d\d-\d\d-\d\d\b")
NUM_STEP_RE = re.compile(r"^\s*\d+\.\s+\S")
WIKILINK_LINE_RE = re.compile(r"^\s*-\s*\[\[")
INLINE_CODE_RE = re.compile(r"`([^`]+)`")
# Path "nudo" all'inizio di una riga dentro un code-fence (stile blocco struttura):
#   career/         # KB carriera
BARE_PATH_RE = re.compile(r"^([\w\-]+(?:/[\w\-.]+)*/)\s")

# Soglie per i check euristici (oltre = sospetto).
MIN_PROCEDURE_STEPS = 3   # liste numerate consecutive
MIN_CATALOG_LINKS = 8     # righe [[wikilink]] consecutive

# Path da non validare: placeholder, esterni, glob.
SKIP_CHARS = set("<>{}$*?|")


def looks_like_path(tok: str) -> bool:
    """True se il token sembra un riferimento a file/cartella del vault."""
    if any(c in tok for c in SKIP_CHARS):
        return False
    if tok.startswith(("~", "/", "http")):
        return False
    if "{{" in tok or "}}" in tok:
        return False
    return tok.endswith("/") or tok.endswith(".md")


def build_index() -> tuple[set[str], set[str], set[str]]:
    """Indicizza il vault una volta: path file relativi, basename, path cartelle."""
    files_rel: set[str] = set()
    names: set[str] = set()
    dirs_rel: set[str] = set()
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in PRUNE_DIRS]
        rel_dir = os.path.relpath(dirpath, ROOT)
        if rel_dir != ".":
            dirs_rel.add(rel_dir.replace(os.sep, "/"))
        for fn in filenames:
            names.add(fn)
            rel = os.path.relpath(os.path.join(dirpath, fn), ROOT)
            files_rel.add(rel.replace(os.sep, "/"))
    return files_rel, names, dirs_rel


def path_exists(tok: str, index: tuple[set[str], set[str], set[str]]) -> bool:
    files_rel, names, dirs_rel = index
    t = tok.rstrip("/")
    if tok.endswith("/"):
        # Riferimento a cartella: deve essere un path relativo esistente.
        return t in dirs_rel
    if "/" in t:
        # Path file qualificato: confronto esatto.
        return t in files_rel
    # Basename nudo (stile wikilink Obsidian): valido se il file esiste ovunque.
    return t in names


def audit(text: str) -> dict[str, list[str]]:
    findings: dict[str, list[str]] = {
        "date": [],
        "procedure": [],
        "catalogo": [],
        "path": [],
    }

    lines = text.splitlines()
    in_fence = False
    seen_paths: set[str] = set()
    index = build_index()

    num_run_start: int | None = None
    num_run_count = 0
    link_run_start: int | None = None
    link_run_count = 0

    def flush_procedure() -> None:
        nonlocal num_run_start, num_run_count
        if num_run_count >= MIN_PROCEDURE_STEPS and num_run_start is not None:
            findings["procedure"].append(
                f"righe {num_run_start}-{num_run_start + num_run_count - 1}: "
                f"{num_run_count} step numerati consecutivi"
            )
        num_run_start, num_run_count = None, 0

    def flush_catalog() -> None:
        nonlocal link_run_start, link_run_count
        if link_run_count >= MIN_CATALOG_LINKS and link_run_start is not None:
            findings["catalogo"].append(
                f"righe {link_run_start}-{link_run_start + link_run_count - 1}: "
                f"{link_run_count} wikilink consecutivi (sembra un catalogo)"
            )
        link_run_start, link_run_count = None, 0

    for i, line in enumerate(lines, start=1):
        stripped = line.strip()

        if stripped.startswith("```"):
            in_fence = not in_fence
            flush_procedure()
            flush_catalog()
            # I path nudi (blocco struttura) vivono dentro i fence: li raccogliamo lì.
            continue

        # --- path reference check (ovunque: anche dentro i fence) ---
        candidates: list[str] = list(INLINE_CODE_RE.findall(line))
        if in_fence:
            m = BARE_PATH_RE.match(line)
            if m:
                candidates.append(m.group(1))
        for tok in candidates:
            tok = tok.strip()
            if looks_like_path(tok) and tok not in seen_paths:
                seen_paths.add(tok)
                if not path_exists(tok, index):
                    findings["path"].append(f"riga {i}: `{tok}` non esiste nel vault")

        if in_fence:
            continue

        # --- date check (solo prosa, fuori dai fence) ---
        if DATE_RE.search(line):
            findings["date"].append(f"riga {i}: {stripped[:80]}")

        # --- procedure check (liste numerate consecutive) ---
        if NUM_STEP_RE.match(line):
            if num_run_start is None:
                num_run_start = i
            num_run_count += 1
        else:
            flush_procedure()

        # --- catalog check (wikilink consecutivi) ---
        if WIKILINK_LINE_RE.match(line):
            if link_run_start is None:
                link_run_start = i
            link_run_count += 1
        else:
            flush_catalog()

    flush_procedure()
    flush_catalog()
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Auditor anti-drift per CLAUDE.md")
    parser.add_argument("--file", default="CLAUDE.md", help="file da auditare")
    parser.add_argument("--strict", action="store_true", help="exit 1 se trova problemi")
    args = parser.parse_args()

    target = ROOT / args.file
    if not target.exists():
        # Niente file = niente drift. Silenzioso: l'hook non deve fallire.
        return 0

    findings = audit(target.read_text(encoding="utf-8", errors="ignore"))
    total = sum(len(v) for v in findings.values())

    if total == 0:
        print(f"✅ {args.file}: nessun drift rilevato")
        return 0

    labels = {
        "path": ("🔗 Riferimenti a path inesistenti (rename non propagato?)",
                 "Aggiorna o rimuovi. I rename vanno registrati SOLO in _meta/log.md."),
        "date": ("📅 Fatti datati",
                 "Le date/decisioni vanno in _meta/log.md, non in CLAUDE.md."),
        "procedure": ("🪜 Procedure passo-passo",
                      "Sposta in _meta/procedures.md; in CLAUDE.md lascia una riga di rimando."),
        "catalogo": ("📚 Cataloghi / liste lunghe",
                     "I cataloghi vivono in _meta/index.md (auto-generato) o taxonomy.md."),
    }

    print(f"⚠️  {args.file}: {total} possibili segni di drift\n")
    for key in ("path", "date", "procedure", "catalogo"):
        items = findings[key]
        if not items:
            continue
        title, hint = labels[key]
        print(f"{title}")
        for it in items:
            print(f"   • {it}")
        print(f"   → {hint}\n")

    return 1 if args.strict else 0


if __name__ == "__main__":
    sys.exit(main())
