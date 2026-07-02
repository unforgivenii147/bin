#!/data/data/com.termux/files/usr/bin/env python3
"""
Finds duplicate files in a directory using stringzilla for high-performance SHA256 hashing.
Reports duplicates by their relative paths.
"""

import os
from collections import defaultdict
from pathlib import Path

import click

try:
    from stringzilla import File, Sha256
except ImportError:
    print("Error: 'stringzilla' library not found. Please install it with 'pip install stringzilla'.")
    exit(1)


def get_file_hash(file_path: Path):
    """
    Calculates the SHA256 hash of a file using stringzilla.

    Args:
        file_path (Path): The path to the file.

    Returns:
        str: The hexdigest of the hash, or None if an error occurred.
    """
    sha256 = Sha256()
    try:
        # Memory-map the file using stringzilla
        mapped_file = File(str(file_path))
        # Compute hash
        file_hash = sha256.update(mapped_file).hexdigest()
        return file_hash
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        return None


def find_duplicates(path: Path):
    """
    Recursively scans a directory for duplicate files.

    Args:
        path (Path): The directory to scan.

    Returns:
        int: Total number of duplicate files found (excluding the original in each group).
    """
    files_by_hash = defaultdict(list)
    duplicate_count = 0

    for root, dirs, files in os.walk(path):
        # Skip .git directory to avoid unnecessary scanning
        if ".git" in dirs:
            dirs.remove(".git")

        for file in files:
            file_path = Path(root) / file

            if file_path.is_file():
                file_hash = get_file_hash(file_path)
                if file_hash:
                    files_by_hash[file_hash].append(file_path)

    # Report duplicates
    for file_hash, file_paths in files_by_hash.items():
        if len(file_paths) > 1:
            duplicate_count += len(file_paths) - 1
            print(f"Duplicate group (Hash: {file_hash}):")
            for file_path in file_paths:
                try:
                    relative_path = file_path.relative_to(path)
                except ValueError:
                    relative_path = file_path
                print(f"  {relative_path}")
            print()

    return duplicate_count


@click.command()
@click.argument("path", default=".", type=click.Path(exists=True, file_okay=False, dir_okay=True))
def report_duplicates(path) -> None:
    """
    Finds and reports duplicate files in the specified directory.
    Duplicates are identified by their content (SHA256 hash).
    """
    path_obj = Path(path).resolve()
    print(f"Searching for duplicates in: {path_obj}")
    total_dups = find_duplicates(path_obj)

    print("\nSummary:")
    print(f"Total redundant files found: {total_dups}")
    print("Process completed.")


if __name__ == "__main__":
    report_duplicates()
