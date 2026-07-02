#!/data/data/com.termux/files/usr/bin/env python3
"""
Cleanup script to remove temporary Python files and directories.

This module scans a directory recursively and removes common temporary
files like .pyc, .log, and directories like __pycache__, build, etc.
It uses multiprocessing for faster execution on large projects.
"""

import os
import pathlib
import shutil
from multiprocessing import Pool, cpu_count
from typing import Iterator, List

# File extensions to delete
FILE_EXTENSIONS: List[str] = [".pyc", ".log", ".bak"]
# Directory names to delete
DIR_NAMES: List[str] = ["__pycache__", "dist", "target", "build"]


def remove_path(path: str) -> None:
    """
    Remove a file or directory at the given path.

    Args:
        path: The string path to the file or directory.
    """
    p = pathlib.Path(path)
    try:
        if p.is_file():
            p.unlink()
            print(f"Removed file: {p}")
        elif p.is_dir():
            shutil.rmtree(p)
            print(f"Removed directory: {p}")
    except Exception as e:
        print(f"Failed to remove {p}: {e}")


def scan_and_remove(base_path: pathlib.Path) -> Iterator[str]:
    """
    Scan the directory recursively and yield matching paths for removal.

    Args:
        base_path: The starting directory path.

    Yields:
        Paths of files and directories that match the cleanup criteria.
    """
    for root, dirs, files in os.walk(base_path, topdown=True):
        # Remove matching files
        for file in files:
            if any(file.endswith(ext) for ext in FILE_EXTENSIONS):
                yield os.path.join(root, file)

        # Remove matching directories
        # We iterate over a copy of dirs to safely remove items from it
        for d in list(dirs):
            if d in DIR_NAMES:
                full_dir_path = os.path.join(root, d)
                
                # Safety check for site-packages
                if "site-packages" in full_dir_path:
                    print(f"Skipping protected directory: {full_dir_path}")
                    continue
                
                yield full_dir_path
                # Remove from dirs list so os.walk doesn't recurse into it
                dirs.remove(d)


def main() -> None:
    """
    Main entry point for the cleanup script.
    """
    base_path = pathlib.Path(os.getcwd()).resolve()
    print(f"Scanning for cleanup in: {base_path}")

    # Use multiprocessing pool for parallel removal
    # We collect paths first to avoid issues with modifying the tree while walking
    paths_to_remove = list(scan_and_remove(base_path))
    
    if not paths_to_remove:
        print("No temporary files or directories found.")
        return

    print(f"Found {len(paths_to_remove)} items to remove. Starting cleanup...")
    
    with Pool(cpu_count()) as pool:
        pool.map(remove_path, paths_to_remove)
    
    print("Cleanup completed.")


if __name__ == "__main__":
    main()
