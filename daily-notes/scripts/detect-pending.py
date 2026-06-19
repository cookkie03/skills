#!/usr/bin/env python3
"""
detect-pending.py — trova i source raw nuovi/modificati dall'ultimo ingest.

Deterministico. Confronta lo stato attuale del vault con la baseline registrata
in _meta/ingest-ledger.json. NON usa l'autore dei commit per attribuire i file
all'utente: il Stop hook fa `git add -A`, quindi un file creato dall'utente può
finire in un commit "ai:". L'unico segnale affidabile è "cos'è cambiato dall'ultimo
ingest registrato" — ed è quello che misura questo script.

Scope: _raw/daily-notes, _raw/articles, _raw/notes (solo quelle esistenti).
Esclude _raw/archived (già processato).

Output: JSON su stdout. Le daily note modificate includono le righe aggiunte dalla
baseline, così l'ingest lavora solo sul delta e non ri-processa il già fatto.

Uso (dalla root del vault):
  python3 scripts/detect-pending.py [--days N] [--include-uncommitted]
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path.cwd()
LEDGER = ROOT / "_meta" / "ingest-ledger.json"

SCOPE_DIRS = ["_raw/daily-notes", "_raw/articles", "_raw/notes"]
EXCLUDE = "_raw/archived"
TEXT_EXT = {".md", ".txt"}


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], capture_output=True, text=True
    ).stdout


def commit_exists(sha: str) -> bool:
    return subprocess.run(
        ["git", "cat-file", "-e", f"{sha}^{{commit}}"],
        capture_output=True,
    ).returncode == 0


def read_ledger() -> dict:
    if LEDGER.exists():
        try:
            return json.loads(LEDGER.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def resolve_baseline(days: int) -> tuple[str | None, str]:
    """Ritorna (commit_baseline, motivazione)."""
    ledger = read_ledger()
    sha = ledger.get("last_ingest_commit")
    if sha and commit_exists(sha):
        return sha, "ultimo ingest registrato nel ledger"
    # Fallback: nessun ledger valido → finestra temporale.
    since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    fallback = git("rev-list", "-1", f"--before={since}", "HEAD").strip()
    if fallback:
        return fallback, f"nessun ledger: baseline = ultimo commit prima di {since}"
    return None, "nessun ledger e storia git troppo corta: tutto è considerato pending"


def in_scope(path: str) -> bool:
    if path.startswith(EXCLUDE):
        return False
    return any(path.startswith(d) for d in SCOPE_DIRS)


def added_lines(baseline: str, path: str) -> list[str]:
    """Righe aggiunte a `path` dalla baseline (solo `+`, esclusi gli header)."""
    diff = git("diff", "--unified=0", baseline, "HEAD", "--", path)
    out = []
    for line in diff.splitlines():
        if line.startswith("+") and not line.startswith("+++"):
            out.append(line[1:])
    return out


def is_daily(path: str) -> bool:
    return path.startswith("_raw/daily-notes")


def needs_preprocess(path: str) -> bool:
    return Path(path).suffix.lower() not in TEXT_EXT


def collect(baseline: str | None, include_uncommitted: bool) -> dict:
    entries: dict[str, str] = {}  # path -> status

    if baseline:
        diff = git("diff", "--name-status", baseline, "HEAD")
        for line in diff.splitlines():
            parts = line.split("\t")
            status = parts[0][0]  # A, M, D, R...
            path = parts[-1]      # per i rename prendiamo la destinazione
            if status != "D" and in_scope(path):
                entries[path] = status
    else:
        # Nessuna baseline: tutto ciò che è in scope è pending.
        for d in SCOPE_DIRS:
            for p in sorted((ROOT / d).rglob("*")) if (ROOT / d).is_dir() else []:
                if p.is_file():
                    rel = str(p.relative_to(ROOT))
                    if in_scope(rel):
                        entries[rel] = "A"

    if include_uncommitted:
        status = git("status", "--porcelain", "--", *SCOPE_DIRS)
        for line in status.splitlines():
            code, path = line[:2], line[3:].strip()
            if "->" in path:  # rename
                path = path.split("->")[-1].strip()
            if in_scope(path) and not code.startswith("D"):
                entries.setdefault(path, "M")

    daily_notes, sources, preprocess = [], [], []
    for path, status in sorted(entries.items()):
        if needs_preprocess(path):
            preprocess.append({"path": path, "status": status})
        elif is_daily(path):
            note = {"path": path, "status": status}
            if status == "M" and baseline:
                note["added_lines"] = added_lines(baseline, path)
            else:
                note["full"] = True  # nuova o senza baseline: leggi tutto
            daily_notes.append(note)
        else:
            sources.append({"path": path, "status": status})

    return {"daily_notes": daily_notes, "sources": sources, "preprocess": preprocess}


def main() -> int:
    ap = argparse.ArgumentParser(description="Rileva source raw pending dall'ultimo ingest")
    ap.add_argument("--days", type=int, default=7, help="finestra fallback se manca il ledger")
    ap.add_argument("--include-uncommitted", action="store_true",
                    help="includi anche i file non ancora committati da Obsidian")
    args = ap.parse_args()

    if not (ROOT / ".git").exists():
        print(json.dumps({"error": "non sono nella root di un repo git"}))
        return 1

    baseline, why = resolve_baseline(args.days)
    head = git("rev-parse", "HEAD").strip()
    buckets = collect(baseline, args.include_uncommitted)

    total = sum(len(v) for v in buckets.values())
    result = {
        "baseline": baseline,
        "baseline_reason": why,
        "head": head,
        "total_pending": total,
        **buckets,
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
