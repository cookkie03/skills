#!/usr/bin/env python3
"""Normalize yt-dlp / gallery-dl metadata JSON files into a common shape."""
import json
import re
from pathlib import Path

HASHTAG_RE = re.compile(r"#(\w+)")


def extract_hashtags(*texts: str | None) -> list[str]:
    tags: list[str] = []
    for text in texts:
        if not text:
            continue
        for tag in HASHTAG_RE.findall(text):
            if tag not in tags:
                tags.append(tag)
    return tags


def from_yt_dlp(info: dict) -> dict:
    caption = info.get("description") or info.get("title")
    autore = info.get("uploader") or info.get("uploader_id") or info.get("channel")
    data = info.get("upload_date")  # YYYYMMDD
    if data and len(data) == 8:
        data = f"{data[:4]}-{data[4:6]}-{data[6:]}"
    like = info.get("like_count")
    durata = info.get("duration")
    hashtag = extract_hashtags(caption, *(info.get("tags") or []))
    return {"caption": caption, "autore": autore, "data": data, "like": like, "hashtag": hashtag, "durata": durata}


def from_gallery_dl(info: dict) -> dict:
    caption = info.get("description") or info.get("content")
    autore = info.get("username") or info.get("uploader") or info.get("author", {}).get("username") if isinstance(info.get("author"), dict) else info.get("username")
    data = info.get("date")
    if isinstance(data, dict):
        data = data.get("date")
    if data:
        data = str(data)[:10]
    like = info.get("likes") or info.get("like_count")
    durata = info.get("duration")
    hashtag = extract_hashtags(caption, *(info.get("tags") or info.get("hashtags") or []))
    return {"caption": caption, "autore": autore, "data": data, "like": like, "hashtag": hashtag, "durata": durata}


def merge(base: dict, extra: dict) -> dict:
    """Fill in missing fields of base from extra, and sum/collect durata."""
    out = dict(base)
    for k, v in extra.items():
        if k == "durata":
            continue
        if out.get(k) in (None, "", []) and v not in (None, "", []):
            out[k] = v
    durs = [d for d in (base.get("durata"), extra.get("durata")) if d]
    out["durata"] = sum(durs) if durs else None
    return out


def load_info_files(info_files: list[str]) -> dict:
    """Read every metadata JSON and merge into a single normalized record."""
    merged: dict = {"caption": None, "autore": None, "data": None, "like": None, "hashtag": [], "durata": None}
    for path in info_files:
        raw = json.loads(Path(path).read_text())
        if "extractor" in raw or "upload_date" in raw or "webpage_url" in raw:
            parsed = from_yt_dlp(raw)
        else:
            parsed = from_gallery_dl(raw)
        merged = merge(merged, parsed)
        for tag in parsed.get("hashtag") or []:
            if tag not in merged["hashtag"]:
                merged["hashtag"].append(tag)
    return merged
