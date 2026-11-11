#!/usr/bin/env python3
"""
Preprocess Office / structured documents for wiki ingest.

Scansiona le cartelle/file passati e per ogni documento Office o strutturato
(docx, pptx, xlsx, e affini) lo converte in Markdown con markitdown.
Salva il risultato come <nome-file-completo>.md accanto all'originale.
Esempio: "Report Q3.docx" -> "Report Q3.docx.md"

markitdown preserva titoli, tabelle, liste e struttura, così wiki-ingest può
leggere il contenuto come testo normale.

Idempotente: se il .md esiste ed è più recente del documento sorgente, salta.

Uso:
    python preprocess-office.py                 # scansiona ./raw
    python preprocess-office.py raw inbox       # più cartelle
    python preprocess-office.py report.docx     # singolo file
    python preprocess-office.py --dry-run        # mostra senza scrivere
"""

from __future__ import annotations

import argparse
import datetime
import sys
from pathlib import Path

# Formati Office e strutturati che markitdown sa convertire in modo affidabile.
# I formati binari legacy (.doc/.ppt/.xls) richiedono spesso una conversione
# preliminare con LibreOffice: vedi nota in fondo.
DOC_EXTS = {
    ".docx",
    ".pptx",
    ".xlsx",
    ".doc",
    ".ppt",
    ".xls",
    ".odt",
    ".odp",
    ".ods",
    ".rtf",
    ".epub",
    ".csv",
    ".tsv",
    ".html",
    ".htm",
    ".xml",
    ".json",
    ".ipynb",
}

LEGACY_BINARY = {".doc", ".ppt", ".xls"}


def load_markitdown():
    """Importa markitdown o esce con istruzioni di installazione."""
    try:
        from markitdown import MarkItDown  # type: ignore
    except ImportError:
        print(
            "❌ 'markitdown' non installato.\n"
            "   Installa con:  pip install 'markitdown[all]'\n"
            "   (l'extra [all] abilita docx, pptx, xlsx, epub e gli altri formati)",
            file=sys.stderr,
        )
        sys.exit(1)
    return MarkItDown()


def output_path(doc: Path) -> Path:
    # <nome-completo>.md — preserva l'estensione originale nello stem,
    # così è sempre chiaro da quale documento deriva la conversione.
    return doc.with_suffix(doc.suffix + ".md")


def is_up_to_date(doc: Path, out: Path) -> bool:
    return out.exists() and out.stat().st_mtime >= doc.stat().st_mtime


def convert(md, doc: Path) -> str | None:
    try:
        result = md.convert(str(doc))
    except Exception as exc:  # markitdown solleva eccezioni eterogenee
        print(f"❌ markitdown error for {doc}:\n   {exc}", file=sys.stderr)
        return None
    text = (result.text_content or "").strip()
    if not text:
        print(f"⚠️  nessun testo estratto da {doc.name}", file=sys.stderr)
        return None
    return text


def process(md, doc: Path, dry_run: bool = False) -> bool:
    out = output_path(doc)
    if is_up_to_date(doc, out):
        print(f"⏭️  {doc.name} (up to date)")
        return True

    if doc.suffix.lower() in LEGACY_BINARY:
        print(
            f"⚠️  {doc.name}: formato binario legacy. Se markitdown fallisce, "
            f"converti prima con LibreOffice:\n"
            f"   libreoffice --headless --convert-to docx \"{doc}\""
        )

    print(f"📄  {doc}")
    if dry_run:
        print(f"   → would create {out.name}")
        return True

    print("   🔄 converting → markdown …")
    text = convert(md, doc)
    if text is None:
        return False

    frontmatter = (
        "---\n"
        f'source_document: "{doc.name}"\n'
        f"converted_at: {datetime.datetime.now().isoformat()}\n"
        "tool: markitdown\n"
        "---\n\n"
        f"# {doc.stem}\n\n"
        f"{text}\n"
    )
    out.write_text(frontmatter, encoding="utf-8")
    print(f"   ✅ {out.name}")
    return True


def iter_docs(paths: list[str]):
    for raw in paths:
        p = Path(raw)
        if p.is_file():
            if p.suffix.lower() in DOC_EXTS:
                yield p
        elif p.is_dir():
            for path in sorted(p.rglob("*")):
                if path.is_file() and path.suffix.lower() in DOC_EXTS:
                    # Salta gli output già generati da questa skill.
                    if path.name.endswith(".md"):
                        continue
                    yield path
        else:
            print(f"⚠️  percorso non trovato: {p}", file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert Office / structured documents to Markdown for wiki ingest"
    )
    parser.add_argument(
        "paths",
        nargs="*",
        default=["raw"],
        help="File o cartelle da processare (default: raw)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Mostra cosa verrebbe fatto senza eseguire",
    )
    args = parser.parse_args()

    md = None if args.dry_run else load_markitdown()

    processed = skipped = failed = 0
    for doc in iter_docs(args.paths):
        if is_up_to_date(doc, output_path(doc)):
            skipped += 1
            continue
        if process(md, doc, dry_run=args.dry_run):
            processed += 1
        else:
            failed += 1

    print(f"\nFatto: {processed} processati, {skipped} già aggiornati, {failed} errori")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
