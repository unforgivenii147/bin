#!/usr/bin/env python3
"""
A script to organize files in a directory into subfolders based on their file sizes.
"""

import os
import shutil
from pathlib import Path


def get_all_files(root_dir):
    """
    Recursively collects all files in the given directory with their sizes.

    Args:
        root_dir (Path): The root directory to search.

    Returns:
        list: A list of tuples (filepath, size) sorted by size.
    """
    files = []
    for root, _, filenames in os.walk(root_dir):
        for filename in filenames:
            filepath = Path(root) / filename
            # Avoid moving the script itself if it's in the same directory
            if filepath.name == "foldesize.py":
                continue
            try:
                if filepath.is_file():
                    size = filepath.stat().st_size
                    files.append((filepath, size))
            except OSError:
                continue
    return sorted(files, key=lambda x: x[1])


def create_size_folders(base_dir, target_count=20):
    """
    Creates folder names based on file size ranges and ensures they exist.

    Args:
        base_dir (Path): The directory where folders will be created.
        target_count (int): The number of folders to create.

    Returns:
        list: A list of tuples (min_size, max_size, folder_name).
    """
    folders = []
    size = 0
    step = 1024 * 1024  # 1MB initial step
    
    for i in range(target_count):
        if i < 5:
            next_size = size + 100 * 1024  # 100KB steps for small files
        elif i < 10:
            next_size = size + 1024 * 1024  # 1MB steps
        else:
            next_size = size + 10 * 1024 * 1024 # 10MB steps
            
        folder_name = f"{size // 1024}k-{next_size // 1024}k"
        if size >= 1024 * 1024:
            folder_name = f"{size // (1024*1024)}M-{next_size // (1024*1024)}M"
            
        folders.append((size, next_size, folder_name))
        folder_path = base_dir / folder_name
        folder_path.mkdir(exist_ok=True)
        size = next_size
        
    # Add a catch-all folder for very large files
    final_folder = "Large_Files"
    (base_dir / final_folder).mkdir(exist_ok=True)
    folders.append((size, float('inf'), final_folder))
    
    return folders


def distribute_files(files, folders, base_dir):
    """
    Distributes files into the appropriate size-based folders.

    Args:
        files (list): List of (filepath, size) tuples.
        folders (list): List of (min_size, max_size, folder_name) tuples.
        base_dir (Path): The base directory for destination folders.
    """
    for filepath, size in files:
        target_folder_name = "Large_Files"
        for min_s, max_s, folder_name in folders:
            if min_s <= size < max_s:
                target_folder_name = folder_name
                break
        
        dest_folder = base_dir / target_folder_name
        # Don't move if it's already in a size folder
        if filepath.parent.name == target_folder_name:
            continue
            
        dest_path = dest_folder / filepath.name
        
        # Handle filename collisions
        counter = 1
        while dest_path.exists():
            dest_path = dest_folder / f"{filepath.stem}_{counter}{filepath.suffix}"
            counter += 1

        try:
            shutil.move(str(filepath), str(dest_path))
            print(f"Moved {filepath.name} ({size} bytes) to {target_folder_name}")
        except Exception as e:
            print(f"Failed to move {filepath}: {e}")


def main():
    """
    Main function to organize files by size.
    """
    base_dir = Path(".").resolve()
    print(f"Processing files in: {base_dir}")

    files = get_all_files(base_dir)
    if not files:
        print("No files found.")
        return

    print(f"Found {len(files)} files.")

    # Create size-based folders
    folders = create_size_folders(base_dir)

    print(f"Organizing files into {len(folders)} folders...")
    distribute_files(files, folders, base_dir)
    print("Organization complete!")


if __name__ == "__main__":
    main()
