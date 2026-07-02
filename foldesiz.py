#!/usr/bin/env python3
"""
A script to organize files into subfolders based on their size distribution.
Unlike foldesize.py, this script tries to create folders that contain an equal 
number of files by calculating size percentiles.
"""

import os
import shutil
from pathlib import Path


def format_size(size):
    """
    Converts a size in bytes to a human-readable string.

    Args:
        size (int): Size in bytes.

    Returns:
        str: Human-readable size (e.g., 10k, 5M).
    """
    if size < 1000:
        return f"{size}B"
    elif size < 1_000_000:
        return f"{size // 1000}k"
    elif size < 1_000_000_000:
        return f"{size // 1_000_000}M"
    else:
        return f"{size // 1_000_000_000}G"


def get_all_files(root_dir):
    """
    Recursively collects all files in the given directory with their sizes.

    Args:
        root_dir (Path): The root directory.

    Returns:
        list: A list of tuples (filepath, size) sorted by size.
    """
    files = []
    root_path = Path(root_dir)
    for root, dirs, filenames in os.walk(root_path):
        # Prevent infinite recursion by not entering folders we likely created
        dirs[:] = [d for d in dirs if "-" not in d or not (d.endswith("k") or d.endswith("M") or d.endswith("G") or d.endswith("B"))]
        
        for filename in filenames:
            if filename == "foldesiz.py":
                continue
            filepath = Path(root) / filename
            try:
                if filepath.is_file():
                    size = filepath.stat().st_size
                    files.append((filepath, size))
            except OSError:
                continue
    return sorted(files, key=lambda x: x[1])


def create_range_folders(base_dir, files, num_folders=10):
    """
    Creates folders based on size ranges that distribute files evenly.

    Args:
        base_dir (Path): The base directory.
        files (list): List of (filepath, size) tuples.
        num_folders (int): Number of folders to create.

    Returns:
        list: A list of tuples (min_size, max_size, folder_name).
    """
    if not files:
        return []

    folder_ranges = []
    files_per_folder = len(files) // num_folders
    if files_per_folder == 0:
        files_per_folder = 1
        num_folders = len(files)

    for i in range(num_folders):
        start_idx = i * files_per_folder
        if i == num_folders - 1:
            end_idx = len(files) - 1
        else:
            end_idx = (i + 1) * files_per_folder - 1
        
        min_size = files[start_idx][1]
        max_size = files[end_idx][1]
        
        folder_name = f"{format_size(min_size)}-{format_size(max_size)}"
        # Handle cases where min and max are same
        if min_size == max_size:
            folder_name = f"Size_{format_size(min_size)}"
            
        folder_path = base_dir / folder_name
        folder_path.mkdir(exist_ok=True)
        folder_ranges.append((min_size, max_size, folder_name))

    return folder_ranges


def distribute_files(files, folders, base_dir):
    """
    Moves files into their respective size-range folders.

    Args:
        files (list): List of (filepath, size) tuples.
        folders (list): List of (min_size, max_size, folder_name) tuples.
        base_dir (Path): The base directory.
    """
    moved_count = 0
    for filepath, size in files:
        target_folder = None
        # Since files and folders are both sorted by size, we could optimize this,
        # but for simplicity, we'll just iterate.
        for min_s, max_s, folder_name in folders:
            if min_s <= size <= max_s:
                target_folder = folder_name
                break
        
        if target_folder:
            dest_dir = base_dir / target_folder
            if filepath.parent == dest_dir:
                continue
                
            dest_path = dest_dir / filepath.name
            
            # Collision handling
            counter = 1
            while dest_path.exists():
                dest_path = dest_dir / f"{filepath.stem}_{counter}{filepath.suffix}"
                counter += 1
                
            try:
                shutil.move(str(filepath), str(dest_path))
                moved_count += 1
            except Exception as e:
                print(f"Error moving {filepath}: {e}")
    
    print(f"Successfully moved {moved_count} files.")


def main():
    """
    Main execution function.
    """
    base_dir = Path(".").resolve()
    print(f"Scanning {base_dir}...")
    
    files = get_all_files(base_dir)
    if not files:
        print("No files to process.")
        return
        
    print(f"Found {len(files)} files.")
    
    # Create ~10 folders or fewer if there are few files
    num_folders = min(10, len(files))
    folders = create_range_folders(base_dir, files, num_folders)
    
    distribute_files(files, folders, base_dir)
    print("Done.")


if __name__ == "__main__":
    main()
