#!/usr/bin/env python3
"""
transcribe_audio.py - Robust speech-to-text transcription via OmniRoute STT.
Handles long audio files automatically via chunking (10-min slices) with Groq primary and Debian Faster-Whisper fallback.
"""

import os
import sys
import json
import glob
import shutil
import tempfile
import argparse
import subprocess
import urllib.request
import urllib.error


def resolve_omniroute_credentials():
    """Finds OmniRoute base URL and API key from environment or config."""
    # 1. Direct environment variables
    base_url = os.environ.get("OMNIROUTE_BASE_URL")
    api_key = os.environ.get("OMNIROUTE_API_KEY")

    if base_url and api_key:
        return base_url.rstrip("/"), api_key

    # 2. Search HERMES_CUSTOM_* variables
    for k, v in os.environ.items():
        if k.startswith("HERMES_CUSTOM_") and k.endswith("_API_KEY"):
            # e.g. HERMES_CUSTOM_100_74_207_0_20128_API_KEY
            parts = k[len("HERMES_CUSTOM_"):-len("_API_KEY")].split("_")
            if len(parts) >= 5:
                ip = ".".join(parts[:4])
                port = parts[4]
                return f"http://{ip}:{port}/v1", v

    # 3. Search ~/.hermes/config.yaml
    config_path = os.path.expanduser("~/.hermes/config.yaml")
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                content = f.read()
            import re
            m = re.search(r'base_url:\s*["\']?(http://[0-9.:]+(?:/v1)?)["\']?', content)
            k_m = re.search(r'api_key:\s*["\']?([a-zA-Z0-9_\-\.]+)["\']?', content)
            if m and k_m:
                b = m.group(1).rstrip("/")
                if not b.endswith("/v1"):
                    b += "/v1"
                return b, k_m.group(1)
        except Exception:
            pass

    raise RuntimeError("Could not resolve OmniRoute STT credentials (OMNIROUTE_BASE_URL / API_KEY).")


def get_audio_duration_seconds(file_path: str) -> float:
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        file_path
    ]
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return float(res.stdout.strip())
    except Exception as e:
        print(f"Warning: Could not probe duration for {file_path}: {e}")
        return 0.0


def transcribe_single_file(audio_path: str, base_url: str, api_key: str, model: str) -> str:
    """Uploads a single audio file chunk to OmniRoute STT endpoint using curl subprocess for multipart robustness."""
    url = f"{base_url}/audio/transcriptions"
    cmd = [
        "curl", "-s", "-X", "POST", url,
        "-H", f"Authorization: Bearer {api_key}",
        "-F", f"file=@{audio_path}",
        "-F", f"model={model}"
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"Curl failed: {res.stderr}")

    try:
        data = json.loads(res.stdout)
        if "text" in data:
            return data["text"]
        elif "error" in data:
            raise RuntimeError(f"API Error ({model}): {data['error']}")
        else:
            raise RuntimeError(f"Unexpected response: {res.stdout[:200]}")
    except json.JSONDecodeError:
        raise RuntimeError(f"Invalid JSON from {url}: {res.stdout[:200]}")


def transcribe_chunk_with_fallback(chunk_path: str, base_url: str, api_key: str) -> str:
    primary_model = "groq/whisper-large-v3-turbo"
    fallback_model = "whisper-local/deepdml/faster-whisper-large-v3-turbo-ct2"

    try:
        return transcribe_single_file(chunk_path, base_url, api_key, primary_model)
    except Exception as e:
        print(f"    [Warning] Primary model '{primary_model}' failed ({e}). Falling back to '{fallback_model}'...")
        return transcribe_single_file(chunk_path, base_url, api_key, fallback_model)


def process_audio_file(audio_path: str, chunk_duration_min: int = 10, output_path: str = None) -> str:
    base_url, api_key = resolve_omniroute_credentials()
    file_name = os.path.basename(audio_path)
    base_name, _ = os.path.splitext(audio_path)

    if output_path is None:
        output_path = f"{base_name}_transcript.md"

    duration = get_audio_duration_seconds(audio_path)
    print(f"\nProcessing '{file_name}' (Duration: {duration / 60:.1f} min)...")

    # If shorter than 10 minutes, transcribe directly
    if 0 < duration <= (chunk_duration_min * 60):
        text = transcribe_chunk_with_fallback(audio_path, base_url, api_key)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text.strip() + "\n")
        print(f"Transcribed successfully -> '{output_path}'")
        return output_path

    # Chunk long audio into temporary directory
    temp_dir = tempfile.mkdtemp(prefix="audio_chunks_")
    try:
        chunk_pattern = os.path.join(temp_dir, "chunk_%03d.mp3")
        chunk_secs = chunk_duration_min * 60
        print(f"  Slicing into {chunk_duration_min}-minute segments...")

        split_cmd = [
            "ffmpeg", "-y", "-i", audio_path,
            "-f", "segment", "-segment_time", str(chunk_secs),
            "-c", "copy", chunk_pattern
        ]
        subprocess.run(split_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

        chunks = sorted(glob.glob(os.path.join(temp_dir, "chunk_*.mp3")))
        print(f"  Created {len(chunks)} chunks. Transcribing sequentially...")

        full_texts = []
        for i, chunk in enumerate(chunks):
            print(f"  - Chunk {i + 1}/{len(chunks)}...")
            chunk_text = transcribe_chunk_with_fallback(chunk, base_url, api_key)
            full_texts.append(chunk_text.strip())

        combined_transcript = " ".join(full_texts).strip() + "\n"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(combined_transcript)

        print(f"Complete! Full transcript ({len(combined_transcript):,} chars) saved to '{output_path}'")
        return output_path

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def main():
    parser = argparse.ArgumentParser(description="Transcribe audio recordings using OmniRoute STT with chunking and fallback.")
    parser.add_argument("target", help="Audio file or folder containing recordings (.m4a, .mp3, .wav, .aac, .webm, .ogg).")
    parser.add_argument("--chunk-min", type=int, default=10, help="Chunk length in minutes for long audio (default: 10).")
    parser.add_argument("-o", "--output", default=None, help="Explicit output path for single file.")
    args = parser.parse_args()

    audio_exts = (".m4a", ".mp3", ".wav", ".aac", ".webm", ".ogg")

    if os.path.isfile(args.target):
        process_audio_file(args.target, chunk_duration_min=args.chunk_min, output_path=args.output)
    elif os.path.isdir(args.target):
        found = False
        for root, _, files in os.walk(args.target):
            for f in sorted(files):
                if f.lower().endswith(audio_exts) and not f.startswith("."):
                    audio_p = os.path.join(root, f)
                    process_audio_file(audio_p, chunk_duration_min=args.chunk_min)
                    found = True
        if not found:
            print(f"No audio files found in {args.target}")
    else:
        print(f"Invalid target: {args.target}")
        sys.exit(1)


if __name__ == "__main__":
    main()
