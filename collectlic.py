#!/data/data/com.termux/files/usr/bin/env python3
"""
Collect all license files in a directory tree.

This module scans a directory recursively for files that likely contain
license information (based on their filename) and aggregates their
contents into a single output file.
"""

import os
from typing import Iterator, Optional
from pathlib import Path

EXCLUDE_DIRS = {".git", "__pycache__"}
OUTPUT_FILE = "/sdcard/all2.txt"


def read_file(path: Path) -> Optional[str]:
    """
    Read the content of a file, ignoring errors.

    Args:
        path: The Path object of the file to read.

    Returns:
        The file content as a string, or None if the file is unreadable.
    """
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return None


def collect_files(root: Path) -> Iterator[Path]:
    """
    Recursively collect files that likely contain license information.

    Args:
        root: The starting directory path.

    Yields:
        Path objects for each matching file.
    """
    for dirpath, dirnames, filenames in os.walk(root):
        # Prune excluded directories
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]

        for fname in filenames:
            full_path = Path(dirpath) / fname
            # skip output file itself and only include if 'license' is in the name
            if "license" not in fname.lower():
                continue
            
            try:
                if full_path.resolve() == Path(OUTPUT_FILE).resolve():
                    continue
            except (OSError, FileNotFoundError):
                pass
                
            yield full_path


def build_all_txt(root_str: str) -> None:
    """
    Aggregate contents of all found license files into the output file.

    Args:
        root_str: The starting directory path as a string.
    """
    root = Path(root_str)
    files = list(collect_files(root))
    print(f"Found {len(files)} potential license files")

    out_path = Path(OUTPUT_FILE)
    try:
        with out_path.open("w", encoding="utf-8") as out:
            for i, path in enumerate(files, 1):
                content = read_file(path)
                if content is None:
                    print(f"Skipping unreadable file: {path}")
                    continue

                # out.write(f"--- FILE: {path} ---\n")
                out.write(content)

                if i != len(files):
                    out.write("\n\n\n")  # 3 empty lines separation

                print(f"Added: {path}")
        print(f"\nFinished: {OUTPUT_FILE} created.")
    except Exception as e:
        print(f"Error writing to output file {OUTPUT_FILE}: {e}")


if __name__ == "__main__":
    build_all_txt(".")
