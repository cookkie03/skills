#!/usr/bin/env python3
"""
Preprocess audio files for wiki ingest.

Scansiona le cartelle raw/, daily-notes/, Clippings/ e per ogni file audio:
- Converte in MP3 se non lo è già (ffmpeg)
- Trascrive con whisper
- Salva la trascrizione come <file>.transcription.md accanto all'originale

Idempotente: se .transcription.md esiste ed è più recente del file audio, salta.
"""

from __future__ import annotations

import argparse
import datetime
import shutil
import subprocess
import sys
from pathlib import Path

AUDIO_EXTS = {".m4a", ".opus", ".wav", ".ogg", ".flac", ".aac", ".wma", ".mp3"}


def check_deps() -> None:
    for tool in ("ffmpeg", "whisper"):
        if shutil.which(tool) is None:
            print(
                f"❌ '{tool}' non trovato. Installa prima di proseguire.\n"
                f"   ffmpeg:  brew install ffmpeg\n"
                f"   whisper: brew install openai-whisper  (o pip install openai-whisper)",
                file=sys.stderr,
            )
            sys.exit(1)


def transcription_path(audio: Path) -> Path:
    return audio.with_suffix(audio.suffix + ".transcription.md")


def is_up_to_date(audio: Path, tx: Path) -> bool:
    return tx.exists() and tx.stat().st_mtime >= audio.stat().st_mtime


def convert_to_mp3(src: Path, dst: Path) -> bool:
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(src),
        "-vn",
        "-ar",
        "16000",
        "-ac",
        "1",
        "-c:a",
        "libmp3lame",
        "-q:a",
        "2",
        str(dst),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"❌ ffmpeg error for {src}:\n{res.stderr}", file=sys.stderr)
        return False
    return True


def transcribe(mp3: Path, out_dir: Path) -> str | None:
    cmd = [
        "whisper",
        str(mp3),
        "--model",
        "turbo",
        "--output_format",
        "txt",
        "--output_dir",
        str(out_dir),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"❌ whisper error for {mp3}:\n{res.stderr}", file=sys.stderr)
        return None

    txt = out_dir / (mp3.stem + ".txt")
    if not txt.exists():
        print(f"❌ whisper output missing: {txt}", file=sys.stderr)
        return None

    text = txt.read_text(encoding="utf-8")
    txt.unlink()
    return text


def process(audio: Path, dry_run: bool = False) -> bool:
    tx = transcription_path(audio)
    if is_up_to_date(audio, tx):
        print(f"⏭️  {audio.name} (up to date)")
        return True

    print(f"🎙️  {audio}")

    if dry_run:
        print(f"   → would create {tx}")
        return True

    needs_conv = audio.suffix.lower() != ".mp3"
    tmp_mp3 = audio.with_suffix(".tmp.mp3")

    try:
        if needs_conv:
            print("   🔄 converting → mp3 …")
            if not convert_to_mp3(audio, tmp_mp3):
                return False

        source = tmp_mp3 if needs_conv else audio
        print("   📝 transcribing …")
        text = transcribe(source, audio.parent)
        if text is None:
            return False

        frontmatter = (
            "---\n"
            f'source_audio: "{audio.name}"\n'
            f"transcribed_at: {datetime.datetime.now().isoformat()}\n"
            "tool: whisper\n"
            "model: turbo\n"
            "---\n\n"
            f"# Transcription: {audio.stem}\n\n"
            f"{text}\n"
        )
        tx.write_text(frontmatter, encoding="utf-8")
        print(f"   ✅ {tx.name}")
        return True
    finally:
        if needs_conv and tmp_mp3.exists():
            tmp_mp3.unlink()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert and transcribe audio files for wiki ingest"
    )
    parser.add_argument(
        "directories",
        nargs="*",
        default=["raw", "daily-notes", "Clippings"],
        help="Cartelle da scansionare (relativamente a Second-Brain/)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Mostra cosa verrebbe fatto senza eseguire",
    )
    args = parser.parse_args()

    if not args.dry_run:
        check_deps()

    base = Path("Second-Brain")
    processed = skipped = failed = 0

    for d in args.directories:
        dir_path = base / d
        if not dir_path.exists():
            print(f"⚠️  cartella non trovata: {dir_path}")
            continue

        for path in dir_path.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in AUDIO_EXTS:
                continue
            if is_up_to_date(path, transcription_path(path)):
                skipped += 1
                continue
            if process(path, dry_run=args.dry_run):
                processed += 1
            else:
                failed += 1

    print(
        f"\nFatto: {processed} processati, {skipped} già aggiornati, {failed} errori"
    )
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
