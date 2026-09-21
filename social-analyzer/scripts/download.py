#!/usr/bin/env python3
"""Download an Instagram or TikTok URL with the right tool and emit a manifest JSON.

Reels/TikTok videos -> yt-dlp --write-info-json
Instagram posts/carousels (/p/) -> gallery-dl --write-metadata (handles multi-image/video posts)
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

VIDEO_EXTS = {".mp4", ".mov", ".m4v", ".webm"}
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}


def pick_tool(url: str) -> str:
    if "tiktok.com" in url:
        return "yt-dlp"
    if re.search(r"instagram\.com/(reel|reels|tv)/", url):
        return "yt-dlp"
    if "instagram.com/p/" in url:
        return "gallery-dl"
    # Fallback: try yt-dlp first, it covers single-video instagram posts too
    return "yt-dlp"


def run_yt_dlp(url: str, outdir: Path, cookies: str | None, cookies_from_browser: str | None) -> None:
    cmd = [
        "yt-dlp",
        "--write-info-json",
        "--no-playlist",
        "-o",
        str(outdir / "%(id)s.%(ext)s"),
        url,
    ]
    if cookies:
        cmd += ["--cookies", cookies]
    elif cookies_from_browser:
        cmd += ["--cookies-from-browser", cookies_from_browser]
    subprocess.run(cmd, check=True)


def run_gallery_dl(url: str, outdir: Path, cookies: str | None, cookies_from_browser: str | None) -> None:
    cmd = [
        "gallery-dl",
        "--write-metadata",
        "-d",
        str(outdir),
        url,
    ]
    if cookies:
        cmd += ["--cookies", cookies]
    elif cookies_from_browser:
        cmd += ["--cookies-from-browser", cookies_from_browser]
    subprocess.run(cmd, check=True)


def collect_manifest(outdir: Path, tool: str) -> dict:
    media_files = []
    info_files = []
    for p in sorted(outdir.rglob("*")):
        if p.is_dir():
            continue
        if p.suffix.lower() == ".json":
            info_files.append(str(p))
        elif p.suffix.lower() in VIDEO_EXTS or p.suffix.lower() in IMAGE_EXTS:
            media_files.append(str(p))
    return {"tool": tool, "outdir": str(outdir), "media_files": media_files, "info_files": info_files}


def main():
    ap = argparse.ArgumentParser(description="Download an Instagram/TikTok URL and emit a manifest JSON")
    ap.add_argument("url")
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--tool", choices=["yt-dlp", "gallery-dl", "auto"], default="auto")
    ap.add_argument("--cookies", help="Path to a cookies.txt file (Netscape format)")
    ap.add_argument("--cookies-from-browser", help="Browser name to read cookies from, e.g. chrome, firefox")
    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    tool = pick_tool(args.url) if args.tool == "auto" else args.tool
    try:
        if tool == "yt-dlp":
            run_yt_dlp(args.url, outdir, args.cookies, args.cookies_from_browser)
        else:
            run_gallery_dl(args.url, outdir, args.cookies, args.cookies_from_browser)
    except subprocess.CalledProcessError as e:
        # Single-video instagram /p/ posts can fail with gallery-dl auth quirks; try the other tool once.
        fallback = "gallery-dl" if tool == "yt-dlp" else "yt-dlp"
        print(f"[download] {tool} failed ({e}), retrying with {fallback}", file=sys.stderr)
        if fallback == "yt-dlp":
            run_yt_dlp(args.url, outdir, args.cookies, args.cookies_from_browser)
        else:
            run_gallery_dl(args.url, outdir, args.cookies, args.cookies_from_browser)
        tool = fallback

    manifest = collect_manifest(outdir, tool)
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
