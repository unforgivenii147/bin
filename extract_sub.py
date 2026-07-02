#!/usr/bin/env python3
"""
A robust utility to extract all embedded subtitle streams from a video file using ffmpeg and ffprobe.
Supports metadata-based naming (language and title).
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str]) -> str:
    """
    Executes a shell command and returns its stdout.
    
    Args:
        cmd (list[str]): The command to execute as a list of strings.
        
    Returns:
        str: The standard output of the command.
        
    Raises:
        RuntimeError: If the command fails.
    """
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())
    return result.stdout


def probe_subtitles(video_path: Path) -> list[dict]:
    """
    Uses ffprobe to discover all subtitle streams in a video file.
    
    Args:
        video_path (Path): Path to the video file.
        
    Returns:
        list[dict]: A list of dictionaries, each describing a subtitle stream.
    """
    cmd = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "s",
        "-show_entries", "stream=index,codec_name:stream_tags=language,title",
        "-of", "json",
        str(video_path),
    ]
    try:
        output = run_command(cmd)
        return json.loads(output).get("streams", [])
    except Exception as e:
        print(f"Error probing file: {e}", file=sys.stderr)
        return []


def extract_subtitles(video_path: Path, output_dir: Path) -> None:
    """
    Extracts each subtitle stream into a separate file in the output directory.
    
    Args:
        video_path (Path): Path to the source video file.
        output_dir (Path): Directory where extracted subtitles will be saved.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    subs = probe_subtitles(video_path)

    if not subs:
        print("No embedded subtitle streams found.")
        return

    base_name = video_path.stem

    for i, s in enumerate(subs):
        # index is the stream index relative to all streams in the file
        stream_idx = s["index"]
        codec = s.get("codec_name", "sub")
        lang = s.get("tags", {}).get("language", "und")
        title = s.get("tags", {}).get("title", "").replace(" ", "_")

        suffix = f".{lang}"
        if title:
            suffix += f".{title}"

        # Prefer SRT output for standard subtitle formats
        out_ext = "srt" if codec in {"subrip", "srt"} else codec
        out_file = output_dir / f"{base_name}{suffix}.stream_{i}.{out_ext}"

        # -y: overwrite output
        # -map 0:s:{i}: selects the i-th subtitle stream
        cmd = [
            "ffmpeg",
            "-y",
            "-i", str(video_path),
            "-map", f"0:s:{i}",
            str(out_file)
        ]

        try:
            run_command(cmd)
            print(f"Extracted: {out_file.name}")
        except RuntimeError as e:
            print(f"Failed to extract subtitle stream {stream_idx} (index {i}): {e}")


def main():
    """
    Main entry point: parses CLI arguments and initiates extraction.
    """
    parser = argparse.ArgumentParser(description="Extract all embedded subtitles from a video file")
    parser.add_argument("movie", help="Path to the video file")
    parser.add_argument("-o", "--output", default="subtitles", help="Output directory (default: 'subtitles')")

    args = parser.parse_args()
    video_path = Path(args.movie).resolve()
    output_dir = Path(args.output).resolve()

    if not video_path.exists():
        print(f"Error: File not found: {video_path}", file=sys.stderr)
        sys.exit(1)

    extract_subtitles(video_path, output_dir)


if __name__ == "__main__":
    main()
