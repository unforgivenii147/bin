#!/data/data/com.termux/files/usr/bin/env python3
import os
import pathlib
from collections import defaultdict


def hash_folder(folder_path, hash_algorithm="sha256"):
    """Compute the hash of a folder by hashing all its files and subfolders recursively."""
    hasher = hashlib.new(hash_algorithm)
    for root, dirs, files in os.walk(folder_path):
        # Sort files and dirs for consistent hashing
        files.sort()
        dirs.sort()
        for file in files:
            file_path = os.path.join(root, file)
            try:
                with pathlib.Path(file_path).open("rb") as f:
                    while chunk := f.read(8192):
                        hasher.update(chunk)
            except OSError:
                # Skip files that can't be read
                continue
    return hasher.hexdigest()


def find_duplicate_folders(root_dir):
    """Recursively find duplicate folders in root_dir."""
    folder_hashes = defaultdict(list)
    for root, dirs, _files in os.walk(root_dir):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            try:
                folder_hash = hash_folder(dir_path)
                folder_hashes[folder_hash].append(dir_path)
            except Exception:
                pass
    # Filter out non-duplicates
    return {h: paths for h, paths in folder_hashes.items() if len(paths) > 1}


if __name__ == "__main__":
    root_dir = pathlib.Path.cwd()
    duplicates = find_duplicate_folders(root_dir)
    if duplicates:
        for paths in duplicates.values():
            for _path in paths:
                pass
