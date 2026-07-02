#!/usr/bin/env python3
"""
Organizes files in a directory into subfolders named after their first letter (A-Z).
Files starting with non-alphabetic characters are moved to a special 'Other' folder.
"""

import os
import pathlib
import shutil
import sys
import argparse


def folderize_files(target_dir: str = ".") -> None:
    """
    Organizes files in the specified directory alphabetically.
    Only affects files directly in target_dir (non-recursive).
    """
    root = pathlib.Path(target_dir).resolve()
    if not root.is_dir():
        print(f"Error: {root} is not a directory.")
        return

    other_folder_name = "Other_Symbols_Or_Numbers"

    # Iterate through entries in the directory
    for entry in root.iterdir():
        # Skip directories and hidden files
        if entry.is_dir() or entry.name.startswith("."):
            continue
        
        # Skip the script itself if it's in the same directory
        if entry.resolve() == pathlib.Path(__file__).resolve():
            continue

        # Determine the target folder name
        first_char = entry.name[0]
        if first_char.isalpha():
            folder_name = first_char.upper()
        else:
            folder_name = other_folder_name

        # Create target folder
        target_folder = root / folder_name
        try:
            target_folder.mkdir(exist_ok=True)
        except OSError as e:
            print(f"Error creating folder {target_folder}: {e}")
            continue

        # Move the file
        try:
            shutil.move(str(entry), str(target_folder / entry.name))
        except (shutil.Error, OSError) as e:
            print(f"Error moving {entry.name}: {e}")


def main() -> None:
    """
    Main entry point. Handles arguments and user confirmation.
    """
    parser = argparse.ArgumentParser(description="Organize files alphabetically into subfolders.")
    parser.add_argument("directory", nargs="?", default=".", help="Directory to organize (default: current)")
    parser.add_argument("-y", "--yes", action="store_true", help="Skip confirmation prompt")

    args = parser.parse_args()

    if not args.yes:
        confirm = input(f"Organize files in '{args.directory}' alphabetically? (Type 'YES' to continue): ")
        if confirm.upper() != "YES":
            print("Operation cancelled.")
            return

    folderize_files(args.directory)
    print("Done.")


if __name__ == "__main__":
    main()
