#!/usr/bin/env python3
"""Recursively replaces text in file contents and renames files/folders.

This script is useful when refactoring a project or changing its name.
It updates all occurrences of a string within files and renames any
files or directories that contain the target string in their name.

Usage:
    change_project_name <text_to_change> <replacement_text>

Example:
    change_project_name oldname newname
"""

import os
import shutil
import sys
from pathlib import Path


def replace_in_file(file_path: Path, old: str, new: str) -> None:
    """Updates file content by replacing the target string.

    Args:
        file_path: Path object to the file.
        old: The string to be replaced.
        new: The replacement string.
    """
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        if old not in content:
            return

        new_content = content.replace(old, new)
        file_path.write_text(new_content, encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        pass


def rename_path(path: Path, old: str, new: str) -> Path:
    """Renames a file or directory if it contains the target string.

    Args:
        path: Path object to the file or directory.
        old: The string to be replaced in the name.
        new: The replacement string.

    Returns:
        The new Path object if renamed, otherwise the original Path.
    """
    if old not in path.name:
        return path

    new_name = path.name.replace(old, new)
    new_path = path.with_name(new_name)

    if new_path.exists():
        print(f"Warning: '{new_path}' already exists. Skipping rename for '{path}'.")
        return path

    try:
        shutil.move(str(path), str(new_path))
        return new_path
    except OSError as e:
        print(f"Error renaming '{path}' to '{new_path}': {e}")
        return path


def main() -> None:
    """Main execution function to handle content replacement and renaming."""
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <text_to_change> <replacement_text>")
        sys.exit(1)

    old_str = sys.argv[1]
    new_str = sys.argv[2]

    # Phase 1: Replace contents in all files
    for path in Path(".").rglob("*"):
        if path.is_file():
            replace_in_file(path, old_str, new_str)

    # Phase 2: Rename files & folders (bottom-up to avoid invalidating paths)
    # We use os.walk because Path.rglob doesn't easily support bottom-up
    for root, dirs, files in os.walk(".", topdown=False):
        for name in files:
            rename_path(Path(root) / name, old_str, new_str)
        for name in dirs:
            rename_path(Path(root) / name, old_str, new_str)


if __name__ == "__main__":
    main()
