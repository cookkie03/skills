#!/usr/bin/env python3
"""End-to-end pipeline: download an Instagram/TikTok URL, transcribe any video,
and emit a compact JSON: {caption, autore, data, like, hashtag, durata, transcript}.

By default downloaded media is deleted at the end; use --keep-media to archive it.
"""
import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
VIDEO_EXTS = {".mp4", ".mov", ".m4v", ".webm"}

sys.path.insert(0, str(SCRIPT_DIR))
from metadata import load_info_files  # noqa: E402


def run_download(url: str, outdir: Path, cookies: str | None, cookies_from_browser: str | None) -> dict:
    cmd = [sys.executable, str(SCRIPT_DIR / "download.py"), url, "--outdir", str(outdir)]
    if cookies:
        cmd += ["--cookies", cookies]
    if cookies_from_browser:
        cmd += ["--cookies-from-browser", cookies_from_browser]
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    return json.loads(result.stdout)


def run_transcribe(video_path: str, model: str, language: str | None) -> str:
    cmd = [sys.executable, str(SCRIPT_DIR / "transcribe.py"), video_path, "--model", model]
    if language:
        cmd += ["--language", language]
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    return result.stdout.strip()


def main():
    ap = argparse.ArgumentParser(description="Analyze an Instagram/TikTok URL end-to-end")
    ap.add_argument("url")
    ap.add_argument("--cookies", help="Path to a cookies.txt file (Netscape format) for private/age-gated content")
    ap.add_argument("--cookies-from-browser", help="Browser to read cookies from, e.g. chrome, firefox")
    ap.add_argument("--whisper-model", default="small", help="faster-whisper model size")
    ap.add_argument("--language", default=None, help="Force transcription language code, e.g. it")
    ap.add_argument("--keep-media", action="store_true", help="Archive downloaded media instead of deleting it")
    ap.add_argument("--archive-dir", default=None, help="Directory to move media into when --keep-media is set")
    args = ap.parse_args()

    workdir = Path(tempfile.mkdtemp(prefix="social-analyzer-"))
    try:
        manifest = run_download(args.url, workdir, args.cookies, args.cookies_from_browser)
        meta = load_info_files(manifest["info_files"])

        transcripts = []
        video_files = [f for f in manifest["media_files"] if Path(f).suffix.lower() in VIDEO_EXTS]
        for video in video_files:
            try:
                text = run_transcribe(video, args.whisper_model, args.language)
                if text:
                    transcripts.append(text)
            except subprocess.CalledProcessError as e:
                print(f"[analyze] transcription failed for {video}: {e.stderr}", file=sys.stderr)

        output = {
            "caption": meta.get("caption"),
            "autore": meta.get("autore"),
            "data": meta.get("data"),
            "like": meta.get("like"),
            "hashtag": meta.get("hashtag"),
            "durata": meta.get("durata"),
            "transcript": " ".join(transcripts).strip() if transcripts else None,
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))

        if args.keep_media:
            dest = Path(args.archive_dir) if args.archive_dir else Path.cwd() / "archive"
            dest.mkdir(parents=True, exist_ok=True)
            for item in workdir.iterdir():
                shutil.move(str(item), str(dest / item.name))
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


if __name__ == "__main__":
    main()
