#!/data/data/com.termux/files/usr/bin/env python3

import hashlib
import os
from collections import defaultdict
from pathlib import Path

import click


# Function to calculate the hash of a file
def get_file_hash(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


# Function to find and delete duplicates in a directory
def find_and_delete_duplicates(path: Path):
    files_by_hash = defaultdict(list)
    duplicate_count = 0
    deleted_count = 0
    total_deleted_size = 0

    # Walk through the directory recursively
    for root, _, files in os.walk(path):
        for file in files:
            file_path = Path(root) / file
            try:
                # Get file hash
                file_hash = get_file_hash(file_path)
                files_by_hash[file_hash].append(file_path)
            except Exception as e:
                print(f"Error processing file {file_path}: {e}")
                continue

    # For each group of files with the same hash, keep the newest and delete the rest
    for file_hash, file_paths in files_by_hash.items():
        if len(file_paths) > 1:
            duplicate_count += len(file_paths) - 1  # Count the duplicates (all but one)

            # Sort files by modification time (newest first)
            file_paths.sort(key=lambda x: x.stat().st_mtime, reverse=True)

            # Keep the newest file, and delete the rest
            for file_to_delete in file_paths[1:]:
                try:
                    file_size = file_to_delete.stat().st_size
                    print(os.path.relpath(file_to_delete))
                    # os.remove(file_to_delete)
                    deleted_count += 1
                    total_deleted_size += file_size
                except Exception as e:
                    print(f"Error deleting file {file_to_delete}: {e}")
        else:
            continue

    return duplicate_count, deleted_count, total_deleted_size


@click.command()
@click.argument(
    "path", default=".", type=click.Path(exists=True, file_okay=False, dir_okay=True)
)
def remove_duplicates(path) -> None:
    """Finds and deletes duplicate files in the specified directory, keeping only the newest one."""
    print(f"Searching for duplicates in directory: {path}")
    duplicate_count, deleted_count, total_deleted_size = find_and_delete_duplicates(
        Path(path)
    )

    # Report results
    print("\nSummary:")
    print(f"dup found: {deleted_count}")
    print(f"del  size: {total_deleted_size} bytes")


if __name__ == "__main__":
    remove_duplicates()
