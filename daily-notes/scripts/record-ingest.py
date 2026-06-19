#!/usr/bin/env python3
"""
record-ingest.py — chiude un ciclo di ingest: archivia i source e avanza il ledger.

Deterministico. Va eseguito a FINE skill, dopo che le pagine tematiche sono state
aggiornate. Fa due cose:

  1. ARCHIVIA i source analizzati: sposta articoli/note in _raw/archived/
     preservando il sotto-path (es. _raw/articles/x.md → _raw/archived/articles/x.md).
     Usa `git mv` così la mossa è tracciata. Le DAILY NOTES non si archiviano mai
     (sono continue): passa solo articoli/note in --archive.

  2. AVANZA il ledger _meta/ingest-ledger.json: last_ingest_commit = HEAD attuale
     (o lo SHA passato con --commit) + una voce di history. Da questa baseline la
     prossima detection escluderà tutto ciò che è già stato ingestato.

Uso (dalla root del vault):
  python3 scripts/record-ingest.py --note "ingest daily 2026-06-19" \
      --archive _raw/articles/foo.md _raw/notes/bar.md
  python3 scripts/record-ingest.py --note "solo daily note, niente da archiviare"
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()
LEDGER = ROOT / "_meta" / "ingest-ledger.json"
ARCHIVE_ROOT = "_raw/archived"
ARCHIVABLE_PREFIXES = ("_raw/articles", "_raw/notes")
DAILY_PREFIX = "_raw/daily-notes"


def git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], capture_output=True, text=True)


def archive(paths: list[str]) -> tuple[list[str], list[str]]:
    moved, skipped = [], []
    for p in paths:
        src = Path(p)
        if p.startswith(DAILY_PREFIX):
            skipped.append(f"{p} (daily note: non si archivia)")
            continue
        if not p.startswith(ARCHIVABLE_PREFIXES):
            skipped.append(f"{p} (fuori da articles/notes: non tocco)")
            continue
        if not (ROOT / src).exists():
            skipped.append(f"{p} (non esiste)")
            continue
        # _raw/articles/sub/x.md → _raw/archived/articles/sub/x.md
        rel_inside_raw = Path(*src.parts[1:])  # toglie "_raw/"
        dest = ROOT / ARCHIVE_ROOT / rel_inside_raw
        dest.parent.mkdir(parents=True, exist_ok=True)
        res = git("mv", str(src), str(dest.relative_to(ROOT)))
        if res.returncode == 0:
            moved.append(f"{p} → {dest.relative_to(ROOT)}")
        else:
            # fallback non-git (file non ancora tracciato)
            try:
                src.rename(dest)
                moved.append(f"{p} → {dest.relative_to(ROOT)} (mv)")
            except OSError as e:
                skipped.append(f"{p} (errore: {e})")
    return moved, skipped


def update_ledger(commit: str, note: str) -> None:
    data = {}
    if LEDGER.exists():
        try:
            data = json.loads(LEDGER.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            data = {}
    now = datetime.now().strftime("%Y-%m-%dT%H:%M")
    history = data.get("history", [])
    history.append({"commit": commit, "at": now, "note": note})
    data["last_ingest_commit"] = commit
    data["last_ingest_at"] = now
    data["history"] = history[-50:]  # tieni corta la storia
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    LEDGER.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Archivia source e avanza il ledger di ingest")
    ap.add_argument("--note", default="", help="descrizione breve dell'ingest")
    ap.add_argument("--commit", default=None, help="SHA baseline (default: HEAD attuale)")
    ap.add_argument("--archive", nargs="*", default=[], help="source da spostare in _raw/archived/")
    args = ap.parse_args()

    if not (ROOT / ".git").exists():
        print("errore: non sono nella root di un repo git", file=sys.stderr)
        return 1

    moved, skipped = archive(args.archive)
    commit = args.commit or git("rev-parse", "HEAD").stdout.strip()
    update_ledger(commit, args.note)

    print(f"✅ ledger aggiornato → baseline {commit[:8]} ({args.note or 'senza nota'})")
    if moved:
        print(f"📦 archiviati ({len(moved)}):")
        for m in moved:
            print(f"   • {m}")
    if skipped:
        print(f"⏭️  non archiviati ({len(skipped)}):")
        for s in skipped:
            print(f"   • {s}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
