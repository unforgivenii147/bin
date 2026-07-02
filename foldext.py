#!/usr/bin/env python3
"""
A script to organize files into subfolders based on their file extensions.
All files from subdirectories are moved to extension-named folders in the base directory.
"""

import os
import shutil
from pathlib import Path


def folderize_by_extension(base_dir: Path):
    """
    Moves files in base_dir and its subdirectories into folders named after their extensions.

    Args:
        base_dir (Path): The root directory to organize.
    """
    no_ext_dir = base_dir / "_no_ext"
    script_name = Path(__file__).name

    for root, dirs, files in os.walk(base_dir):
        root_path = Path(root)
        
        # Identify extension folders in the base directory to avoid recursing into them
        # We only want to skip folders that are directly under base_dir and represent an extension
        if root_path == base_dir:
            # We don't skip anything in the base_dir itself, but we will skip them in next iterations
            pass
        elif root_path.parent == base_dir:
            # If we are in a direct subdirectory of base_dir, and it's not a hidden folder,
            # we might want to process it unless it's one of our target extension folders.
            # For simplicity, we process all subdirectories but skip moving files if they
            # are already in their correct destination.
            pass

        for filename in files:
            if filename == script_name:
                continue

            src_path = root_path / filename
            
            # Extract extension
            ext = src_path.suffix.lower().lstrip(".")
            target_folder_name = ext if ext else "_no_ext"
            target_dir = base_dir / target_folder_name

            # Skip if already in the correct destination folder at the base level
            if src_path.parent == target_dir:
                continue

            target_dir.mkdir(exist_ok=True)
            dest_path = target_dir / filename

            # Avoid overwriting files with the same name
            counter = 1
            while dest_path.exists():
                dest_path = target_dir / f"{src_path.stem}_{counter}{src_path.suffix}"
                counter += 1

            try:
                shutil.move(str(src_path), str(dest_path))
                print(f"Moved: {src_path.relative_to(base_dir)} -> {target_folder_name}/")
            except Exception as e:
                print(f"Error moving {src_path}: {e}")

    # Clean up empty directories
    for root, dirs, files in os.walk(base_dir, topdown=False):
        for name in dirs:
            dir_path = Path(root) / name
            try:
                if not any(dir_path.iterdir()):
                    dir_path.rmdir()
            except OSError:
                pass


if __name__ == "__main__":
    BASE_DIRECTORY = Path(".").resolve()
    print(f"Organizing files in {BASE_DIRECTORY} by extension...")
    folderize_by_extension(BASE_DIRECTORY)
    print("Done.")
