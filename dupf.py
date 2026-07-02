#!/data/data/com.termux/files/usr/bin/env python3
"""
Finds and optionally deletes duplicate files in a directory.
Uses MD5 hashing for speed and keeps the newest version of a file in each duplicate group.
"""

import hashlib
import os
from collections import defaultdict
from pathlib import Path

import click


def get_file_hash(file_path: Path):
    """
    Calculates the MD5 hash of a file.

    Args:
        file_path (Path): The path to the file.

    Returns:
        str: The MD5 hexdigest.
    """
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except (PermissionError, OSError) as e:
        print(f"Error reading {file_path}: {e}")
        return None


def find_and_process_duplicates(path: Path, delete: bool):
    """
    Scans a directory for duplicates and optionally deletes them.

    Args:
        path (Path): The directory to scan.
        delete (bool): Whether to actually delete the files.

    Returns:
        tuple: (duplicate_count, deleted_count, total_deleted_size)
    """
    files_by_hash = defaultdict(list)
    duplicate_count = 0
    deleted_count = 0
    total_deleted_size = 0

    for root, _, files in os.walk(path):
        for file in files:
            file_path = Path(root) / file
            file_hash = get_file_hash(file_path)
            if file_hash:
                files_by_hash[file_hash].append(file_path)

    for file_hash, file_paths in files_by_hash.items():
        if len(file_paths) > 1:
            duplicate_count += len(file_paths) - 1

            # Sort by modification time (newest first)
            file_paths.sort(key=lambda x: x.stat().st_mtime, reverse=True)

            # Keep the newest file, process the rest
            for file_to_delete in file_paths[1:]:
                try:
                    file_size = file_to_delete.stat().st_size
                    rel_path = os.path.relpath(file_to_delete, path)
                    
                    if delete:
                        print(f"Deleting: {rel_path}")
                        os.remove(file_to_delete)
                    else:
                        print(f"Duplicate found: {rel_path}")
                    
                    deleted_count += 1
                    total_deleted_size += file_size
                except Exception as e:
                    print(f"Error processing {file_to_delete}: {e}")

    return duplicate_count, deleted_count, total_deleted_size


@click.command()
@click.argument("path", default=".", type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option("--delete", is_flag=True, help="Actually delete duplicate files.")
def remove_duplicates(path, delete) -> None:
    """
    Finds duplicate files in a directory. 
    By default, it only reports them. Use --delete to remove them.
    Keeps the most recently modified file in each group.
    """
    path_obj = Path(path).resolve()
    print(f"Scanning directory: {path_obj}")
    if delete:
        print("MODE: DELETE (Keeping newest files)")
    else:
        print("MODE: REPORT ONLY")

    dup_found, del_count, del_size = find_and_process_duplicates(path_obj, delete)

    print("\nSummary:")
    print(f"Duplicates found: {dup_found}")
    if delete:
        print(f"Files deleted: {del_count}")
        print(f"Space freed: {del_size / 1024 / 1024:.2f} MB")
    else:
        print(f"Potential space to free: {del_size / 1024 / 1024:.2f} MB")


if __name__ == "__main__":
    remove_duplicates()
