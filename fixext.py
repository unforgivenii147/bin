#!/usr/bin/env python3
"""
Corrects file extensions based on MIME type detection and text content heuristics.
Uses 'python-magic' for MIME detection and provides heuristics for plain text files.
"""

import os
import sys
import argparse
from pathlib import Path

try:
    import magic
except ImportError:
    print("Error: 'python-magic' is required. Install it with 'pip install python-magic'.")
    sys.exit(1)

# Base MIME → extension mapping
MIME_TO_EXT = {
    "text/html": "html",
    "application/json": "json",
    "application/javascript": "js",
    "application/pdf": "pdf",
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/gif": "gif",
    "image/webp": "webp",
    "image/svg+xml": "svg",
    "application/zip": "zip",
    "application/gzip": "gz",
    "application/x-tar": "tar",
    "text/xml": "xml",
    "application/xml": "xml",
    "application/x-sh": "sh",
    "application/x-python": "py",
    "text/x-python": "py",
    "audio/mpeg": "mp3",
    "audio/wav": "wav",
    "video/mp4": "mp4",
}


def detect_text_based_extension(text: str) -> str:
    """
    Heuristic detection for text-based files when MIME is 'text/plain'.
    """
    text = text.strip()
    text_lower = text.lower()

    # Python
    if text.startswith("#!") and "python" in text:
        return "py"
    if any(k in text for k in ["def ", "class ", "import ", "from ", "if __name__ == "]):
        return "py"

    # Shell
    if text.startswith("#!") and any(sh in text for sh in ["sh", "bash", "zsh"]):
        return "sh"

    # Markdown
    if text.startswith("# ") or text.startswith("## ") or (text.startswith("---") and "\ntitle:" in text):
        return "md"

    # YAML
    if text.startswith("---") or (": " in text and "\n" in text and not text.startswith("[")):
        return "yaml"

    # TOML
    if "[" in text and "]" in text and "=" in text:
        return "toml"

    # INI
    if text.startswith("[") and "]" in text and "=" in text:
        return "ini"

    # SQL
    if any(text_lower.startswith(cmd) for cmd in ["select ", "insert ", "update ", "delete ", "create ", "alter "]):
        return "sql"

    # CSS
    if "{" in text and "}" in text and ":" in text and ";" in text:
        return "css"

    # CSV
    if "," in text and "\n" in text and text.count(",") > text.count("\n"):
        return "csv"

    # XML
    if text.startswith("<?xml"):
        return "xml"

    return ""


def detect_extension(path: Path, mime_type: str) -> str:
    """
    Detects the appropriate extension for a file based on its MIME type or content.
    """
    if mime_type in MIME_TO_EXT:
        return MIME_TO_EXT[mime_type]

    if mime_type == "text/plain":
        try:
            with open(path, "r", errors="ignore") as f:
                sample = f.read(4096)
            guessed = detect_text_based_extension(sample)
            if guessed:
                return guessed
        except OSError:
            pass

    return ""


def safe_rename(src: Path, dst: Path) -> Path:
    """
    Renames a file from src to dst, avoiding collisions by appending a counter.
    """
    if not dst.exists():
        src.rename(dst)
        return dst

    base = dst.stem
    ext = dst.suffix
    counter = 1

    new_path = dst.with_name(f"{base} ({counter}){ext}")
    while new_path.exists():
        counter += 1
        new_path = dst.with_name(f"{base} ({counter}){ext}")

    src.rename(new_path)
    return new_path


def correct_file_extensions(root_dir: str = ".", dry_run: bool = False) -> None:
    """
    Walks through the root directory and corrects file extensions.
    """
    try:
        mime_detector = magic.Magic(mime=True)
    except Exception as e:
        print(f"Error initializing magic: {e}")
        return

    root_path = Path(root_dir)
    for path in root_path.rglob("*"):
        if not path.is_file() or path.is_symlink():
            continue

        try:
            mime_type = mime_detector.from_file(str(path))
        except Exception:
            print(f"Skipping unreadable: {path}")
            continue

        new_ext = detect_extension(path, mime_type)
        if not new_ext:
            continue

        current_ext = path.suffix.lower().lstrip(".")
        if current_ext == new_ext:
            continue
        
        # Handle cases where new_ext is jpg and current_ext is jpeg
        if (new_ext == "jpg" and current_ext == "jpeg") or (new_ext == "jpeg" and current_ext == "jpg"):
            continue

        new_name = f"{path.stem}.{new_ext}"
        new_path = path.with_name(new_name)

        if dry_run:
            print(f"[DRY-RUN] Would rename: {path.name}  →  {new_name}")
        else:
            print(f"Renaming: {path.name}  →  {new_name}")
            final_path = safe_rename(path, new_path)
            if final_path != new_path:
                print(f" ⚠  Collision detected. Saved as: {final_path.name}")


def main() -> None:
    """
    Main entry point. Parses arguments and starts extension correction.
    """
    parser = argparse.ArgumentParser(description="Correct file extensions based on MIME type.")
    parser.add_argument("directory", nargs="?", default=".", help="Directory to process (default: current)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be renamed without doing it")
    args = parser.parse_args()

    correct_file_extensions(args.directory, args.dry_run)


if __name__ == "__main__":
    main()
