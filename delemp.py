#!/usr/bin/env python3
"""
Recursive Empty-Line Cleaner.
Removes or collapses consecutive blank lines in text files recursively.
Features concurrent processing and extension-based filtering.
"""

import os
import sys
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# Configuration
MAX_WORKERS = os.cpu_count() or 8
TEXT_CHUNK = 8192
EXCLUDED_DIRS = {".git", "__pycache__", ".venv", "node_modules"}

# Default locations for whitelist/blacklist files (can be overridden by user)
# These were previously hardcoded to /sdcard/
DEFAULT_WHITELIST_PATH = Path("/sdcard/txt")
DEFAULT_BLACKLIST_PATH = Path("/sdcard/bin")


def load_extensions(file_path: Path) -> set[str]:
    """
    Loads a set of file extensions from a text file.

    Args:
        file_path: Path to the file containing extensions (one per line).

    Returns:
        A set of normalized extensions (e.g., {'.txt', '.py'}).
    """
    if not file_path.exists():
        # Fallback to local file if /sdcard is not available
        local_path = Path.cwd() / file_path.name
        if not local_path.exists():
            return set()
        file_path = local_path

    exts = set()
    try:
        for line in file_path.read_text().splitlines():
            line = line.strip().lower()
            if not line or line.startswith("#"):
                continue
            # Ensure extension starts with a dot
            exts.add(f".{line.lstrip('.')}")
    except Exception as e:
        print(f"Warning: Could not load extensions from {file_path}: {e}")
    return exts


def is_text_file(path: Path) -> bool:
    """
    Checks if a file is likely a text file by looking for null bytes in the first chunk.

    Args:
        path: Path to the file.

    Returns:
        True if the file appears to be text, False otherwise.
    """
    try:
        with open(path, "rb") as f:
            chunk = f.read(TEXT_CHUNK)
            return b"\x00" not in chunk
    except OSError:
        return False


def clean_lines(lines: list[str], collapse: bool) -> tuple[list[str], int]:
    """
    Processes a list of lines to remove or collapse blank lines.

    Args:
        lines: List of strings representing file lines.
        collapse: If True, keep at most one consecutive blank line. 
                  If False, remove all blank lines.

    Returns:
        A tuple containing (list of cleaned lines, number of lines removed).
    """
    removed = 0
    if not lines:
        return [], 0

    if not collapse:
        cleaned = [l for l in lines if l.strip()]
        removed = len(lines) - len(cleaned)
        return cleaned, removed

    cleaned = []
    blank_run = 0

    for line in lines:
        if line.strip():
            blank_run = 0
            cleaned.append(line)
        else:
            blank_run += 1
            if blank_run == 1:
                cleaned.append(line)
            else:
                removed += 1

    return cleaned, removed


def clean_file(path: Path, whitelist: set[str], blacklist: set[str], collapse: bool) -> tuple[bool, int, str]:
    """
    Cleans blank lines from a single file if it meets criteria.

    Args:
        path: Path to the file.
        whitelist: Set of allowed extensions.
        blacklist: Set of forbidden extensions.
        collapse: Whether to collapse or remove all blank lines.

    Returns:
        A tuple of (changed_boolean, count_removed, extension_string).
    """
    ext = path.suffix.lower()
    
    if (blacklist and ext in blacklist) or (whitelist and ext not in whitelist):
        return False, 0, ""

    if not is_text_file(path):
        return False, 0, ""

    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()

        cleaned, removed = clean_lines(lines, collapse)

        if removed == 0:
            return False, 0, ""

        with open(path, "w", encoding="utf-8", errors="ignore") as f:
            f.writelines(cleaned)

        return True, removed, ext
    except Exception:
        return False, 0, ""


def iter_files(root: Path):
    """
    Yields all files in the root directory recursively, excluding specified directories.
    """
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDED_DIRS]
        for name in filenames:
            yield Path(dirpath) / name


def main() -> None:
    """
    Main function for the recursive empty-line cleaner.
    """
    collapse = "--collapse" in sys.argv
    
    whitelist = load_extensions(DEFAULT_WHITELIST_PATH)
    blacklist = load_extensions(DEFAULT_BLACKLIST_PATH)
    
    if not whitelist:
        print("Note: No whitelist found. Processing based on text detection and blacklist.")

    root = Path.cwd()
    total_removed = 0
    modified_files_count = 0
    per_ext_stats = defaultdict(int)

    files = list(iter_files(root))
    print(f"Scanning {len(files)} files...")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(clean_file, f, whitelist, blacklist, collapse): f for f in files}

        for future in as_completed(futures):
            try:
                changed, removed, ext = future.result()
                if changed:
                    modified_files_count += 1
                    total_removed += removed
                    per_ext_stats[ext] += removed
            except Exception as e:
                print(f"Error processing a file: {e}")

    print("\n✓ Clean-up complete")
    print(f"  Files modified: {modified_files_count}")
    print(f"  Blank lines removed: {total_removed}")

    if per_ext_stats:
        print("\n  Per-extension stats:")
        for ext, count in sorted(per_ext_stats.items()):
            print(f"    {ext}: {count}")


if __name__ == "__main__":
    main()
