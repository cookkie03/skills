#!/usr/bin/env python3
"""
check-frontmatter.py — auditor deterministico del frontmatter delle wiki page.

Lo schema è DATA-DRIVEN: viene letto da un blocco machine-readable dentro
_meta/taxonomy.md (fenced ```yaml che inizia con la riga `# frontmatter-schema`).
Così lo stesso script funziona per qualsiasi vault: ogni vault descrive le sue
famiglie di frontmatter in taxonomy.md, qui non c'è nulla di hardcoded.
Se il blocco manca, si usa un default generico minimale (un'unica famiglia).

Cosa segnala (warn-only, exit 0 di default — sicuro per hook):
  1. Pagine senza frontmatter (escluse le cartelle in `exclude_dirs` + ogni dotfolder)
  2. Campi obbligatori mancanti per la famiglia di `type` della pagina
  3. Tag usati ma non registrati nella tabella "Tag per tema" di taxonomy.md
  4. `status`/`type` con valore fuori dall'enum dichiarato per la famiglia

--fix:
  Unico fix automatico: registra in taxonomy.md (tabella Tag per tema) i tag
  non ancora elencati ma usati >= 2 volte nel vault. Tutto il resto richiede
  giudizio umano (non si inventano date o categorie) e resta solo nel report.

Uso:
  python3 _meta/check-frontmatter.py            # warn-only, exit 0
  python3 _meta/check-frontmatter.py --strict   # exit 1 se trova problemi
  python3 _meta/check-frontmatter.py --fix      # registra tag ricorrenti in taxonomy.md
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

try:
    import yaml
except ImportError:
    print("⚠️  PyYAML non disponibile, skip check-frontmatter.py", file=sys.stderr)
    sys.exit(0)

ROOT = Path.cwd()
TAXONOMY_PATH = ROOT / "_meta" / "taxonomy.md"

TAG_ROW_RE = re.compile(r"^\|\s*`([^`]+)`\s*\|")
SCHEMA_FENCE_RE = re.compile(
    r"```ya?ml\s*\n#\s*frontmatter-schema\s*\n(.*?)\n```", re.DOTALL
)
MIN_TAG_USES_TO_AUTOFIX = 2

# Default usato quando taxonomy.md non contiene un blocco frontmatter-schema:
# vault generico, un'unica famiglia. Volutamente minimale.
DEFAULT_SCHEMA = {
    "exclude_dirs": ["_raw", "_models", "_meta", "_scratch", "node_modules"],
    "no_fm_expected": ["AGENTS.md", "CLAUDE.md", "GEMINI.md"],
    "families": [
        {
            "name": "generica",
            "match_path": [],
            "required": ["title", "type", "created", "updated"],
            "type_enum": ["concept", "list", "synthesis", "source",
                          "overview", "master", "meta"],
            "status_enum": ["draft", "reviewed", "verified", "stale", "archived"],
        }
    ],
}


def load_schema() -> dict:
    if not TAXONOMY_PATH.exists():
        return DEFAULT_SCHEMA
    text = TAXONOMY_PATH.read_text(encoding="utf-8")
    m = SCHEMA_FENCE_RE.search(text)
    if not m:
        return DEFAULT_SCHEMA
    try:
        schema = yaml.safe_load(m.group(1))
    except yaml.YAMLError:
        return DEFAULT_SCHEMA
    if not isinstance(schema, dict) or "families" not in schema:
        return DEFAULT_SCHEMA
    schema.setdefault("exclude_dirs", DEFAULT_SCHEMA["exclude_dirs"])
    schema.setdefault("no_fm_expected", DEFAULT_SCHEMA["no_fm_expected"])
    for fam in schema["families"]:
        fam.setdefault("match_path", [])
        fam.setdefault("required", [])
        fam.setdefault("type_enum", [])
        fam.setdefault("status_enum", [])
    return schema


def parse_taxonomy_tags() -> set[str]:
    if not TAXONOMY_PATH.exists():
        return set()
    tags = set()
    in_table = False
    for line in TAXONOMY_PATH.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("## Tag per tema"):
            in_table = True
            continue
        if in_table and line.strip().startswith("##"):
            break
        if in_table:
            m = TAG_ROW_RE.match(line.strip())
            if m:
                tags.add(m.group(1))
    return tags


def iter_pages(exclude_dirs: set[str], no_fm_expected: set[str]) -> list[Path]:
    # Ogni folder che inizia per "." è escluso sistematicamente via startswith(".").
    return [
        p for p in sorted(ROOT.rglob("*.md"))
        if not any(part in exclude_dirs or part.startswith(".")
                   for part in p.relative_to(ROOT).parts)
        and p.name not in no_fm_expected
    ]


def load_frontmatter(path: Path) -> dict | None:
    text = path.read_text(encoding="utf-8", errors="ignore")
    m = re.match(r"^---\n(.*?)\n---\n?", text, re.DOTALL)
    if not m:
        return None
    try:
        fm = yaml.safe_load(m.group(1))
    except yaml.YAMLError:
        return None
    return fm if isinstance(fm, dict) else None


def family_for(rel: str, fm: dict, families: list[dict]) -> dict:
    # Il `type` esistente, se valido per una famiglia, ha priorità sul path:
    # evita che un hub (es. type: overview sotto travel/) venga scambiato per
    # un'altra famiglia solo per via della cartella in cui vive.
    t = fm.get("type")
    if t is not None:
        for fam in families:
            if t in fam["type_enum"]:
                return fam
    for fam in families:
        for prefix in fam["match_path"]:
            if rel.startswith(prefix):
                return fam
    # Fallback: famiglia con match_path vuoto (la "generica"), o l'ultima.
    for fam in families:
        if not fam["match_path"]:
            return fam
    return families[-1]


def audit(schema: dict) -> tuple[dict[str, list[str]], Counter]:
    findings: dict[str, list[str]] = {
        "no_fm": [], "missing_fields": [], "bad_enum": [], "unregistered_tags": []
    }
    known_tags = parse_taxonomy_tags()
    tag_uses: Counter = Counter()
    families = schema["families"]
    exclude_dirs = set(schema["exclude_dirs"])
    no_fm_expected = set(schema["no_fm_expected"])

    for path in iter_pages(exclude_dirs, no_fm_expected):
        rel = str(path.relative_to(ROOT))
        fm = load_frontmatter(path)
        if fm is None:
            raw = path.read_text(encoding="utf-8", errors="ignore")
            if raw.startswith("---\n"):
                findings["no_fm"].append(f"{rel}: frontmatter presente ma YAML non valido")
            else:
                findings["no_fm"].append(f"{rel}: nessun frontmatter")
            continue

        # Board Kanban Obsidian: frontmatter dedicato al plugin, non è una wiki page.
        if "kanban-plugin" in fm:
            tags = fm.get("tags")
            if isinstance(tags, list):
                for tag in tags:
                    tag_uses[tag] += 1
            continue

        fam = family_for(rel, fm, families)
        missing = [f for f in fam["required"] if f not in fm or fm.get(f) in (None, "")]
        if missing:
            findings["missing_fields"].append(f"{rel} [{fam['name']}]: manca {missing}")

        t = fm.get("type")
        if t is not None and t not in fam["type_enum"]:
            findings["bad_enum"].append(
                f"{rel}: type='{t}' non valido per famiglia '{fam['name']}' "
                f"(attesi: {sorted(fam['type_enum'])})")

        s = fm.get("status")
        if s is not None and s not in fam["status_enum"]:
            findings["bad_enum"].append(
                f"{rel}: status='{s}' non valido per famiglia '{fam['name']}' "
                f"(attesi: {sorted(fam['status_enum'])})")

        tags = fm.get("tags")
        if isinstance(tags, list):
            for tag in tags:
                tag_uses[tag] += 1
                root = str(tag).split("/", 1)[0]  # tag annidato: vale la radice
                if tag not in known_tags and root not in known_tags:
                    findings["unregistered_tags"].append(
                        f"{rel}: tag '{tag}' non in taxonomy.md")

    return findings, tag_uses


def fix_taxonomy(tag_uses: Counter, known_tags: set[str]) -> list[str]:
    to_add = sorted(
        t for t, n in tag_uses.items()
        if t not in known_tags and n >= MIN_TAG_USES_TO_AUTOFIX
    )
    if not to_add:
        return []
    lines = TAXONOMY_PATH.read_text(encoding="utf-8").splitlines()
    out, inserted = [], False
    for i, line in enumerate(lines):
        out.append(line)
        if (not inserted and line.strip().startswith("| `")
                and line.strip().endswith("|")
                and i + 1 < len(lines) and not lines[i + 1].strip().startswith("|")):
            for tag in to_add:
                out.append(f"| `{tag}` | _(auto-registrato da check-frontmatter.py --fix — descrizione da rifinire)_ |")
            inserted = True
    TAXONOMY_PATH.write_text("\n".join(out) + "\n", encoding="utf-8")
    return to_add


def main() -> int:
    parser = argparse.ArgumentParser(description="Auditor frontmatter delle wiki page")
    parser.add_argument("--strict", action="store_true", help="exit 1 se trova problemi")
    parser.add_argument("--fix", action="store_true", help="registra tag ricorrenti non ancora in taxonomy.md")
    args = parser.parse_args()

    schema = load_schema()
    findings, tag_uses = audit(schema)

    if args.fix:
        known_tags = parse_taxonomy_tags()
        added = fix_taxonomy(tag_uses, known_tags)
        if added:
            print(f"✅ taxonomy.md: registrati {len(added)} tag nuovi: {added}")
            findings, tag_uses = audit(schema)

    total = sum(len(v) for v in findings.values())
    if total == 0:
        print("✅ check-frontmatter: nessun problema rilevato")
        return 0

    labels = {
        "no_fm": "📄 Pagine senza frontmatter valido",
        "missing_fields": "🧩 Campi obbligatori mancanti",
        "bad_enum": "🚫 Valori fuori enum (type/status)",
        "unregistered_tags": "🏷️  Tag non registrati in taxonomy.md",
    }
    print(f"⚠️  check-frontmatter: {total} problemi rilevati\n")
    for key in ("no_fm", "missing_fields", "bad_enum", "unregistered_tags"):
        items = findings[key]
        if not items:
            continue
        print(labels[key])
        for it in items[:40]:
            print(f"   • {it}")
        if len(items) > 40:
            print(f"   ... e altri {len(items) - 40}")
        print()

    return 1 if args.strict else 0


if __name__ == "__main__":
    sys.exit(main())
