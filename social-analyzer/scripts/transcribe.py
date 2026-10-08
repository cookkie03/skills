#!/usr/bin/env python3
"""Extract audio from a video with ffmpeg and transcribe it with faster-whisper."""
import argparse
import subprocess
import sys
import tempfile
from pathlib import Path


def extract_audio(video_path: Path, audio_path: Path) -> None:
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(video_path),
        "-vn",
        "-ac",
        "1",
        "-ar",
        "16000",
        str(audio_path),
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def transcribe(audio_path: Path, model_size: str, language: str | None) -> tuple[str, float]:
    from faster_whisper import WhisperModel

    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    segments, info = model.transcribe(str(audio_path), language=language, vad_filter=True)
    text = " ".join(seg.text.strip() for seg in segments).strip()
    return text, info.duration


def main():
    ap = argparse.ArgumentParser(description="Extract audio and transcribe a video file")
    ap.add_argument("video", help="Path to the video file")
    ap.add_argument("--model", default="small", help="faster-whisper model size (tiny/base/small/medium/large-v3)")
    ap.add_argument("--language", default=None, help="Force a language code (e.g. it, en); default: auto-detect")
    args = ap.parse_args()

    video_path = Path(args.video)
    if not video_path.exists():
        print(f"Video not found: {video_path}", file=sys.stderr)
        sys.exit(1)

    with tempfile.TemporaryDirectory() as tmp:
        audio_path = Path(tmp) / "audio.wav"
        extract_audio(video_path, audio_path)
        text, duration = transcribe(audio_path, args.model, args.language)

    print(text)
    print(f"[duration_seconds={duration:.1f}]", file=sys.stderr)


if __name__ == "__main__":
    main()
