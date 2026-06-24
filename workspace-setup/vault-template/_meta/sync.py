#!/usr/bin/env python3
"""
_meta/sync.py — sincronizza i file di stato vivi del vault.

Operazioni:
1. Ricostruisce _meta/index.md scansionando tutti i .md del vault
2. Aggiorna la sezione "File toccati di recente" in _meta/hot-cache.md
   leggendo i file modificati dagli ultimi commit "ai:"

Eseguito automaticamente dal Stop hook di Claude Code a fine turno.
Idempotente: rieseguibile senza danni.
"""

from __future__ import annotations

import re
import subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()

# Cartelle SEMPRE escluse dall'index: servizio/diario, non "contenuto" del vault.
# Le cartelle dotfile (.obsidian, .git, .claude, …) sono escluse a parte via
# startswith(".") in is_excluded(), così non serve elencarle tutte.
STRUCTURAL_EXCLUDE = {
    "_meta", "daily-notes", "Daily Notes", "Journal", "Diario",
}

# Schema in taxonomy.md: stesso blocco letto da check-frontmatter.py. Riusiamo il
# suo `exclude_dirs` così "dove non indicizzare" è dichiarato in un solo posto.
SCHEMA_FENCE_RE = re.compile(
    r"```ya?ml\s*\n#\s*frontmatter-schema\s*\n(.*?)\n```", re.DOTALL
)


def load_exclude_dirs() -> set[str]:
    """STRUCTURAL_EXCLUDE ∪ exclude_dirs dichiarati in taxonomy.md (se leggibili)."""
    exclude = set(STRUCTURAL_EXCLUDE)
    taxonomy = ROOT / "_meta" / "taxonomy.md"
    if not taxonomy.exists():
        return exclude
    try:
        import yaml  # opzionale: senza PyYAML restano i soli structural
    except ImportError:
        return exclude
    m = SCHEMA_FENCE_RE.search(taxonomy.read_text(encoding="utf-8", errors="ignore"))
    if not m:
        return exclude
    try:
        schema = yaml.safe_load(m.group(1))
    except yaml.YAMLError:
        return exclude
    if isinstance(schema, dict):
        for d in schema.get("exclude_dirs", []) or []:
            exclude.add(str(d))
    return exclude


EXCLUDE_DIRS = load_exclude_dirs()

# Quanti commit "ai:" recenti leggere per "File toccati di recente"
RECENT_AI_COMMITS = 5


# ── helpers ────────────────────────────────────────────────────────────────────

def is_excluded(rel: Path) -> bool:
    return any(part in EXCLUDE_DIRS or part.startswith(".") for part in rel.parts)


def extract_title(path: Path) -> str:
    try:
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            if line.startswith("# "):
                return line[2:].strip()
    except OSError:
        pass
    return path.stem


def extract_description(path: Path) -> str:
    try:
        in_fm = False
        fm_closed = False
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            s = line.strip()
            if s == "---":
                if not fm_closed:
                    in_fm = not in_fm
                    if not in_fm:
                        fm_closed = True
                    continue
            if in_fm:
                continue
            if s.startswith("#") or not s:
                continue
            return s[:100]
    except OSError:
        pass
    return ""


def git(*args: str) -> str:
    try:
        return subprocess.run(
            ["git", *args], capture_output=True, text=True, check=True
        ).stdout.strip()
    except subprocess.CalledProcessError:
        return ""


# ── index ──────────────────────────────────────────────────────────────────────

def rebuild_index() -> None:
    index_path = ROOT / "_meta" / "index.md"
    if not index_path.exists():
        return

    by_folder: dict[str, list[str]] = {}
    for md in sorted(ROOT.rglob("*.md")):
        rel = md.relative_to(ROOT)
        if is_excluded(rel):
            continue
        folder = str(rel.parent) if str(rel.parent) != "." else "(root)"
        title = extract_title(md)
        desc = extract_description(md)
        wikilink = f"[[{str(rel.with_suffix(''))}]]"
        entry = f"- {wikilink}"
        if title and title != md.stem:
            entry += f" — {title}"
        if desc:
            entry += f": {desc}"
        by_folder.setdefault(folder, []).append(entry)

    lines = [
        "# Index",
        "",
        "Catalogo dei contenuti del vault.",
        f"Aggiornato: {datetime.now().strftime('%Y-%m-%d %H:%M')} da `_meta/sync.py`",
        "",
    ]
    for folder in sorted(by_folder):
        lines += [f"## {folder}/", *by_folder[folder], ""]

    index_path.write_text("\n".join(lines), encoding="utf-8")
    total = sum(len(v) for v in by_folder.values())
    print(f"✅ index.md aggiornato ({total} file)")


# ── hot-cache ──────────────────────────────────────────────────────────────────

def get_recent_ai_files() -> list[str]:
    log = git("log", "--oneline", f"-{RECENT_AI_COMMITS * 4}")
    hashes = [
        line.split()[0]
        for line in log.splitlines()
        if " ai:" in line
    ][:RECENT_AI_COMMITS]

    seen: set[str] = set()
    files: list[str] = []
    for h in hashes:
        for f in git("diff-tree", "--no-commit-id", "-r", "--name-only", h).splitlines():
            if f not in seen and not f.startswith("_meta/"):
                files.append(f)
                seen.add(f)
    return files


def update_hot_cache(ai_files: list[str]) -> None:
    hc_path = ROOT / "_meta" / "hot-cache.md"
    if not hc_path.exists():
        return

    today = datetime.now().strftime("%Y-%m-%d")
    content = hc_path.read_text(encoding="utf-8")
    section = "## File toccati di recente"
    section_exists = section in content

    new_entries = (
        [f"- [[{f}]]" for f in ai_files[:10]]
        if ai_files else ["- (nessuno in questa sessione)"]
    )

    lines = content.splitlines()
    out: list[str] = []
    skipping = False

    for line in lines:
        if line.startswith("**Aggiornato**:"):
            out.append(f"**Aggiornato**: {today}")
            continue
        if line.strip() == section:
            skipping = True
            out.append(line)
            out.extend(new_entries)
            continue
        if skipping:
            if line.startswith("## ") or line.startswith("# "):
                skipping = False
                out.append(line)
            continue
        out.append(line)

    if not section_exists:
        out += ["", section, *new_entries]

    hc_path.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"✅ hot-cache.md aggiornato ({len(ai_files)} file toccati)")


# ── main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    rebuild_index()
    update_hot_cache(get_recent_ai_files())


if __name__ == "__main__":
    main()
