#!/usr/bin/env python3
"""Automatically translates non-English text files to English.

This script scans a directory for text files containing non-ASCII characters,
splits them into chunks, and translates them to English using the
Google Translator API in parallel.
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List

import regex as re
from deep_translator import GoogleTranslator

# Directory to scan
DIRECTORY = "."

# Characters per translation chunk
CHUNK_SIZE = 2000

# Detect non-ASCII characters
NON_ENGLISH_PATTERN = re.compile(r"[^\x00-\x7F]")


def is_text_file(path: Path) -> bool:
    """Checks if a file is likely a text file (not binary).

    Args:
        path: Path object to the file.

    Returns:
        True if the file appears to be text, False otherwise.
    """
    try:
        with path.open("rb") as f:
            chunk = f.read(2048)
        return b"\x00" not in chunk
    except OSError:
        return False


def split_into_chunks(text: str, size: int) -> List[str]:
    """Splits text into chunks of a maximum size.

    Args:
        text: The string to split.
        size: Maximum number of characters per chunk.

    Returns:
        A list of string chunks.
    """
    return [text[i : i + size] for i in range(0, len(text), size)]


def translate_chunk(chunk: str) -> str:
    """Translates a single chunk of text to English.

    Args:
        chunk: The text chunk to translate.

    Returns:
        The translated text, or the original chunk if translation fails.
    """
    try:
        return GoogleTranslator(source="auto", target="en").translate(chunk)
    except Exception as e:
        print(f"[ERROR] Chunk translation failed: {e}")
        return chunk


def contains_non_english(text: str) -> bool:
    """Checks if text contains non-ASCII characters.

    Args:
        text: The string to check.

    Returns:
        True if non-ASCII characters are found, False otherwise.
    """
    return bool(NON_ENGLISH_PATTERN.search(text))


def translate_file(path: Path) -> None:
    """Translates a single file and saves the output.

    Args:
        path: Path object to the file.
    """
    print(f"\n[INFO] Processing file: {path}")

    try:
        with path.open("r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except OSError as e:
        print(f"[ERROR] Cannot read file {path}: {e}")
        return

    if not contains_non_english(content):
        print(f"[SKIP] File is already English (ASCII): {path.name}")
        return

    print(f"[INFO] Non-English content detected in: {path.name}")
    chunks = split_into_chunks(content, CHUNK_SIZE)
    print(f"[INFO] Total chunks: {len(chunks)}")

    print(f"[INFO] Translating chunks in parallel...")
    with ThreadPoolExecutor(max_workers=8) as executor:
        translated_chunks = list(executor.map(translate_chunk, chunks))

    translated_text = "".join(translated_chunks)

    # Output file: {stem}_eng{suffix}
    new_name = f"{path.stem}_eng{path.suffix}"
    new_path = path.parent / new_name

    try:
        with new_path.open("w", encoding="utf-8") as f:
            f.write(translated_text)
        print(f"[DONE] Translated → {new_path.name}")
    except OSError as e:
        print(f"[ERROR] Failed to write output file {new_path}: {e}")


def process_directory(directory: str) -> None:
    """Scans a directory for eligible text files and translates them.

    Args:
        directory: The path to the directory to scan.
    """
    print(f"[INFO] Scanning directory: {directory}")
    root = Path(directory)
    ignore_dirs = {
        ".git", ".venv", "venv", "__pycache__", "node_modules", "build", "dist"
    }

    files: List[Path] = []
    for path in root.rglob("*"):
        # Skip ignored directories and non-files
        if any(part in ignore_dirs for part in path.parts):
            continue
        if path.is_file() and is_text_file(path):
            files.append(path)

    print(f"\n[INFO] Total text files found: {len(files)}")

    print("[INFO] Starting parallel file translation...\n")
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(translate_file, f): f for f in files}
        for future in as_completed(futures):
            f = futures[future]
            try:
                future.result()
            except Exception as e:
                print(f"[ERROR] Unexpected error processing {f}: {e}")


if __name__ == "__main__":
    process_directory(DIRECTORY)
