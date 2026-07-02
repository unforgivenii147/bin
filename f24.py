#!/data/data/com.termux/files/usr/bin/env python3
"""
A utility to scan the current directory and list files created or modified within the last 24 hours.
Uses parallel processing for faster scanning on large directories.
"""

import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Tuple, Optional

try:
    from tqdm import tqdm
except ImportError:
    # Fallback if tqdm is not installed
    def tqdm(iterable, **kwargs):
        return iterable

SECONDS_24H = 24 * 60 * 60
NOW = time.time()
EXCLUDE_DIRS = {".git", "__pycache__", ".idea", ".vscode"}


def iter_files(root: Path) -> List[Path]:
    """
    Collects all file paths under the root directory, excluding specific directories.
    
    Args:
        root (Path): The root directory to scan.
        
    Returns:
        List[Path]: A list of file paths.
    """
    files: List[Path] = []
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        # Filter directories in-place to prune the walk
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        for fname in filenames:
            files.append(Path(dirpath) / fname)
    return files


def ctime_if_recent(path: Path) -> Optional[Tuple[float, Path]]:
    """
    Checks if a file was created or modified within the last 24 hours.
    
    Args:
        path (Path): The file path to check.
        
    Returns:
        Optional[Tuple[float, Path]]: A tuple of (timestamp, path) if recent, else None.
    """
    try:
        # st_ctime is creation time on Windows, but change time on Unix
        # st_mtime is modification time
        stat = path.stat()
        timestamp = max(stat.st_ctime, stat.st_mtime)
        if NOW - timestamp <= SECONDS_24H:
            return timestamp, path
    except (FileNotFoundError, PermissionError, OSError):
        pass
    return None


def main() -> None:
    """
    Main entry point: scans files in parallel and prints those modified in the last 24 hours.
    """
    root = Path.cwd()
    files = iter_files(root)

    if not files:
        print("No files found.")
        return

    recent: List[Tuple[float, Path]] = []

    # Using ThreadPoolExecutor for I/O bound stat calls
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(ctime_if_recent, p) for p in files]

        for fut in tqdm(
            as_completed(futures),
            total=len(futures),
            desc="Scanning",
            unit="file",
        ):
            result = fut.result()
            if result is not None:
                recent.append(result)

    if not recent:
        print("No files modified in the last 24 hours.")
        return

    # Sort by timestamp: oldest to newest (newest last)
    recent.sort(key=lambda x: x[0])

    print(f"\nFiles modified in the last 24 hours ({len(recent)} total):")
    for _, path in recent:
        try:
            print(path.relative_to(root))
        except ValueError:
            print(path)


if __name__ == "__main__":
    main()
