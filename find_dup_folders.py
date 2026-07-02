#!/usr/bin/env python3
"""
Recursively finds duplicate folders in the current directory or a specified path.
A folder is considered a duplicate if it contains the exact same files and subfolder structure.
"""

import hashlib
import os
import pathlib
import sys
from collections import defaultdict


def hash_folder(folder_path: str, cache: dict) -> str:
    """
    Computes the hash of a folder by hashing its contents (files and subfolders).
    Uses a cache to avoid redundant computations in nested structures.
    """
    if folder_path in cache:
        return cache[folder_path]

    hasher = hashlib.sha256()
    
    try:
        # List entries and sort them for consistent hashing
        entries = sorted(os.scandir(folder_path), key=lambda e: e.name)
    except OSError:
        return ""

    for entry in entries:
        hasher.update(entry.name.encode("utf-8"))
        if entry.is_file(follow_symlinks=False):
            try:
                # Hash file content
                with open(entry.path, "rb") as f:
                    while chunk := f.read(8192):
                        hasher.update(chunk)
            except OSError:
                continue
        elif entry.is_dir(follow_symlinks=False):
            # Recursively hash subfolder and update current folder's hasher
            subfolder_hash = hash_folder(entry.path, cache)
            hasher.update(subfolder_hash.encode("utf-8"))

    folder_hash = hasher.hexdigest()
    cache[folder_path] = folder_hash
    return folder_hash


def find_duplicate_folders(root_dir: str) -> dict:
    """
    Finds duplicate folders starting from root_dir using a bottom-up hashing approach.
    """
    folder_hashes = defaultdict(list)
    cache = {}

    # Walk top-down but we use cache to make hash_folder efficient
    for root, dirs, _ in os.walk(root_dir):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            h = hash_folder(dir_path, cache)
            if h:
                folder_hashes[h].append(dir_path)

    return {h: paths for h, paths in folder_hashes.items() if len(paths) > 1}


def main() -> None:
    """
    Main entry point. Finds and prints duplicate folders.
    """
    root_dir = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    print(f"Searching for duplicate folders in: {root_dir}")
    
    duplicates = find_duplicate_folders(root_dir)
    
    if not duplicates:
        print("No duplicate folders found.")
        return

    print(f"Found {len(duplicates)} sets of duplicate folders:\n")
    for h, paths in duplicates.items():
        print(f"Hash: {h}")
        for path in sorted(paths):
            print(f"  - {path}")
        print()


if __name__ == "__main__":
    main()
