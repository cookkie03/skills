---
name: social-analyzer
description: Pipeline to download and analyze Instagram (reels, posts, carousels) and TikTok links. This skill should be used when the user shares an Instagram or TikTok URL and wants its caption, author, date, likes, hashtags, duration, and/or a transcript of any video/audio. Downloads media with yt-dlp/gallery-dl, extracts audio with ffmpeg, transcribes with faster-whisper, returns a compact JSON, and deletes downloaded media unless asked to keep it.
version: 0.1.0
last_updated: 2026-06-29
---

# Social Analyzer (Instagram + TikTok)

## Overview

Given an Instagram or TikTok link, this skill runs the full pipeline end to
end and returns a single compact JSON object:

```json
{"caption": "...", "autore": "...", "data": "2026-06-01", "like": 12345, "hashtag": ["reel", "fyp"], "durata": 23.4, "transcript": "..."}
```

- Reels / TikTok videos → downloaded with `yt-dlp --write-info-json`
- Posts / carousels (`/p/...`) → downloaded with `gallery-dl --write-metadata`
  (handles multiple images/videos in one post)
- Any video found → audio extracted with `ffmpeg`, transcribed with
  `faster-whisper`
- Downloaded media is deleted after analysis unless `--keep-media` is passed

## Requirements

```bash
pip install yt-dlp gallery-dl faster-whisper
# ffmpeg must be available on PATH
```

## Quick start

```bash
python scripts/analyze.py "https://www.instagram.com/reel/XXXXXXXXX/"
python scripts/analyze.py "https://www.tiktok.com/@user/video/XXXXXXXXX"
python scripts/analyze.py "https://www.instagram.com/p/XXXXXXXXX/"
```

This prints the final JSON to stdout. The temp download directory is always
removed when the process exits, including on errors.

## Handling private / login-walled content (auth)

Instagram and TikTok often block anonymous requests (private accounts,
age-gated videos, or generic bot detection). Pass your own session cookies
— this is the supported mechanism in both yt-dlp and gallery-dl, not a
security bypass:

```bash
# From an exported cookies.txt (Netscape format)
python scripts/analyze.py "<url>" --cookies cookies.txt

# Or read directly from an installed browser's cookie store
python scripts/analyze.py "<url>" --cookies-from-browser chrome
```

See `references/auth-cookies.md` for how to export cookies and which
browsers are supported. Only use this for your own account or content you
are authorized to access.

## Options

```
python scripts/analyze.py <url>
  --cookies PATH               cookies.txt for authenticated access
  --cookies-from-browser NAME  read cookies from chrome/firefox/edge/...
  --whisper-model SIZE         tiny|base|small|medium|large-v3 (default: small)
  --language CODE              force transcription language, e.g. it (default: auto-detect)
  --keep-media                 archive downloaded media instead of deleting it
  --archive-dir PATH           where to move media when --keep-media is set (default: ./archive)
```

## Pipeline stages (usable standalone)

Each stage can also be run independently for debugging or custom pipelines:

### 1. Download — `scripts/download.py`
Picks yt-dlp or gallery-dl based on the URL (reel/tv → yt-dlp, `/p/` post →
gallery-dl, with automatic fallback to the other tool on failure), downloads
into `--outdir`, and prints a manifest JSON of media + metadata files:

```bash
python scripts/download.py "<url>" --outdir /tmp/dl --cookies cookies.txt
```

### 2. Metadata normalization — `scripts/metadata.py`
Library module (no CLI) used by `analyze.py` to merge yt-dlp/gallery-dl
metadata JSON files into the common `{caption, autore, data, like, hashtag,
durata}` shape, since the two tools use different field names.

### 3. Transcription — `scripts/transcribe.py`
Extracts mono 16kHz audio with ffmpeg into a temp file, then transcribes
with faster-whisper (CPU, int8):

```bash
python scripts/transcribe.py video.mp4 --model small --language it
```

### 4. Orchestration + cleanup — `scripts/analyze.py`
Ties the above together and removes the temp download directory at the end
(`shutil.rmtree` in a `finally` block), unless `--keep-media` is given.

## Notes on carousels

Instagram carousel posts can mix images and videos. `analyze.py` transcribes
every video found in the post and concatenates the transcripts with spaces;
`hashtag` and `durata` aggregate across all metadata files found. Images
contribute no transcript but are still counted when deciding whether to
keep/delete media.

## Out of scope

This skill does not implement CAPTCHA solving, IP rotation, or other
anti-bot evasion. If a download keeps failing even with valid cookies, the
content is likely not accessible to your account — that's a hard stop, not
something to work around.
