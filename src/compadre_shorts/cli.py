"""Local FFmpeg-based clip preparation for Compadre Shorts Studio v0.2."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def require_binary(name: str) -> str:
    binary = shutil.which(name)
    if not binary:
        raise RuntimeError(f"Required program not found: {name}. Install it with: brew install ffmpeg")
    return binary


def probe_duration(path: Path, ffprobe: str) -> float:
    result = subprocess.run(
        [ffprobe, "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        check=True, capture_output=True, text=True,
    )
    try:
        duration = float(result.stdout.strip())
    except ValueError as exc:
        raise RuntimeError("Could not read video duration with ffprobe.") from exc
    if duration <= 0:
        raise RuntimeError("Input video has no valid duration.")
    return duration


def probe_has_audio(path: Path, ffprobe: str) -> bool:
    result = subprocess.run(
        [ffprobe, "-v", "error", "-select_streams", "a:0",
         "-show_entries", "stream=index", "-of", "csv=p=0", str(path)],
        check=True, capture_output=True, text=True,
    )
    return bool(result.stdout.strip())


def build_segments(total: float, chunk: float, minimum: float) -> list[tuple[float, float]]:
    segments: list[tuple[float, float]] = []
    start = 0.0
    index = 0
    while start < total:
        length = min(chunk, total - start)
        if length < minimum:
            break
        segments.append((start, length))
        index += 1
        start = index * chunk
    return segments


def render_clip(
    ffmpeg: str,
    source: Path,
    destination: Path,
    start: float,
    length: float,
    style: str,
    audio_processing: str,
    has_audio: bool,
) -> None:
    video_filters = [
        "scale=1080:1920:force_original_aspect_ratio=increase",
        "crop=1080:1920",
        "setsar=1",
    ]
    if style == "viral":
        # A restrained punchier grade; no scene understanding or fake captions.
        video_filters.extend([
            "eq=contrast=1.10:saturation=1.20:brightness=0.01",
            "unsharp=5:5:0.55:3:3:0.25",
        ])

    command = [
        ffmpeg, "-hide_banner", "-loglevel", "error", "-y",
        "-ss", f"{start:.3f}", "-i", str(source), "-t", f"{length:.3f}",
        "-map", "0:v:0", "-map", "0:a?",
        "-vf", ",".join(video_filters),
        "-c:v", "libx264", "-preset", "medium", "-crf", "21",
        "-pix_fmt", "yuv420p",
    ]
    if has_audio and audio_processing == "normalize":
        command.extend([
            "-af", "loudnorm=I=-16:TP=-1.5:LRA=11,alimiter=limit=0.95",
        ])
    command.extend([
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart", str(destination),
    ])
    subprocess.run(command, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="compadre-shorts",
        description="Prepare vertical gameplay clips locally with FFmpeg.",
    )
    parser.add_argument("input", type=Path, help="Path to the source gameplay video")
    parser.add_argument("--output", type=Path, default=Path("renders"))
    parser.add_argument("--mode", choices=("sequential", "smart"), default="sequential")
    parser.add_argument("--duration", type=float, default=60.0,
                        help="Target segment duration in seconds (default: 60)")
    parser.add_argument("--min-seconds", type=float, default=15.0,
                        help="Discard a final remainder shorter than this (default: 15)")
    parser.add_argument("--style", choices=("clean", "viral"), default="viral",
                        help="Visual preset: clean or punchier viral grade (default: viral)")
    parser.add_argument("--audio-processing", choices=("original", "normalize"),
                        default="normalize",
                        help="Keep original audio level or apply loudness/peak control")
    args = parser.parse_args()

    try:
        source = args.input.expanduser().resolve()
        if not source.is_file():
            raise RuntimeError(f"Input file does not exist: {source}")
        if args.duration <= 0 or args.min_seconds <= 0:
            raise RuntimeError("--duration and --min-seconds must be greater than zero.")
        if args.min_seconds > args.duration:
            raise RuntimeError("--min-seconds cannot be greater than --duration.")

        ffmpeg = require_binary("ffmpeg")
        ffprobe = require_binary("ffprobe")
        total = probe_duration(source, ffprobe)
        has_audio = probe_has_audio(source, ffprobe)
        segments = build_segments(total, args.duration, args.min_seconds)
        if not segments:
            raise RuntimeError("No segments meet the minimum duration.")

        output_dir = args.output.expanduser().resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
        stem = source.stem
        manifest = {
            "project": "Compadre Shorts Studio",
            "version": "0.2.0",
            "source": str(source),
            "source_duration_seconds": round(total, 3),
            "mode": args.mode,
            "style": args.style,
            "audio_processing": args.audio_processing if has_audio else "no_audio_stream",
            "segment_target_seconds": args.duration,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "editorial_status": "review_required",
            "note": (
                "The smart mode is currently interval-based and does not perform "
                "semantic scene detection."
                if args.mode == "smart"
                else "Sequential interval cuts; review every clip before publishing."
            ),
            "clips": [],
        }

        for number, (start, length) in enumerate(segments, start=1):
            filename = f"{stem}_short_{number:03d}.mp4"
            destination = output_dir / filename
            print(f"[{number}/{len(segments)}] Rendering {filename}")
            render_clip(
                ffmpeg, source, destination, start, length,
                args.style, args.audio_processing, has_audio,
            )
            manifest["clips"].append({
                "file": filename,
                "start_seconds": round(start, 3),
                "duration_seconds": round(length, 3),
                "status": "pending_review",
            })

        manifest_path = output_dir / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
                                 encoding="utf-8")
        print(f"Done. {len(segments)} clips saved in {output_dir}")
        print(f"Manifest: {manifest_path}")
        return 0
    except (RuntimeError, subprocess.CalledProcessError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
