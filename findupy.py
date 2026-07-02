#!/usr/bin/env python3
"""
Finds duplicate files in a directory using file size comparison and SHA256 hashing.
Uses tqdm for progress tracking and supports exporting results to JSON.
"""

import hashlib
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

try:
    from tqdm import tqdm
except ImportError:
    # Fallback if tqdm is not installed
    def tqdm(iterable, **kwargs):
        return iterable

SKIPPED_PATHS = []


def hash_file(path: Path, chunk_size: int = 8192) -> str:
    """
    Computes SHA256 hash of a file.
    Only shows progress bar for files larger than 100MB.
    """
    sha = hashlib.sha256()
    try:
        file_size = path.stat().st_size
        use_pbar = file_size > 100 * 1024 * 1024  # 100MB
        
        with open(path, "rb") as f:
            if use_pbar:
                with tqdm(
                    total=file_size,
                    unit="B",
                    unit_scale=True,
                    unit_divisor=1024,
                    desc=f"Hashing {path.name}",
                    leave=False,
                ) as pbar:
                    for chunk in iter(lambda: f.read(chunk_size), b""):
                        sha.update(chunk)
                        pbar.update(len(chunk))
            else:
                for chunk in iter(lambda: f.read(chunk_size), b""):
                    sha.update(chunk)
    except (PermissionError, OSError):
        SKIPPED_PATHS.append(str(path))
        return None
    return sha.hexdigest()


def find_duplicate_files(directory: str) -> dict:
    """
    Finds duplicate files by first grouping by size and then hashing candidates.
    """
    dir_path = Path(directory)
    if not dir_path.exists():
        print(f"Error: Directory {directory} does not exist.")
        return {}

    # 1. Group files by size
    size_map = defaultdict(list)
    all_files_count = 0
    print(f"📁 Scanning {directory}...")
    for root, _, files in os.walk(dir_path):
        for f in files:
            p = Path(root) / f
            try:
                size_map[p.stat().st_size].append(p)
                all_files_count += 1
            except (PermissionError, OSError):
                SKIPPED_PATHS.append(str(p))

    # 2. Identify candidates for hashing (size groups > 1)
    candidates = [p for paths in size_map.values() if len(paths) > 1 for p in paths]
    if not candidates:
        return {}

    print(f"🔍 Found {len(candidates)} candidate files with matching sizes. Hashing...")
    
    duplicates = defaultdict(list)
    for p in tqdm(candidates, desc="Hashing candidates", unit="file"):
        h = hash_file(p)
        if h:
            duplicates[h].append(str(p))

    return {h: paths for h, paths in duplicates.items() if len(paths) > 1}


def print_duplicates(dups: dict) -> None:
    """
    Prints the found duplicates in a readable format.
    """
    if not dups:
        print("🎉 No duplicates found!")
        return

    print("\n🔍 Duplicate Files Found:\n")
    for i, (h, paths) in enumerate(dups.items(), start=1):
        print(f"Group {i} (hash={h[:12]}...):")
        for p in paths:
            print(f"   • {p}")
        print("-" * 40)


def export_to_json(dups: dict, output_path="duplicates.json") -> None:
    """
    Exports the duplicate groups to a JSON file.
    """
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(dups, f, indent=2)
    print(f"📦 Results exported to {output_path}")


def main() -> None:
    """
    Main entry point. Handles user input and workflow.
    """
    if len(sys.argv) > 1:
        folder = sys.argv[1]
    else:
        folder = input("Enter folder path to scan (default: current): ").strip() or "."
    
    duplicates = find_duplicate_files(folder)
    print_duplicates(duplicates)
    
    if SKIPPED_PATHS:
        print(f"\n⚠️  Skipped {len(SKIPPED_PATHS)} files due to permissions.")
        if input("Show skipped paths? (y/n): ").lower() == "y":
            for p in SKIPPED_PATHS:
                print(f"   • {p}")

    if duplicates:
        save = input("\nExport results to JSON? (y/n): ").lower().strip()
        if save == "y":
            export_to_json(duplicates)


if __name__ == "__main__":
    main()
