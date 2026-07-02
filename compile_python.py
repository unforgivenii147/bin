#!/data/data/com.termux/files/usr/bin/env python3
"""
Clean up and compile Python files in the Termux environment.

This module scans the Python library directory, removes compiled bytecode files (.pyc),
and re-compiles directories that are not part of site-packages or other excluded paths.
"""

import os
import compileall
from pathlib import Path
from typing import Set


def remove_pyc_file(fpath: str) -> bool:
    """
    Remove a .pyc file if it exists and is not in a protected directory.

    Args:
        fpath: The path to the file.

    Returns:
        True if the file was removed or skipped due to protection, False otherwise.
    """
    filepath = Path(fpath)
    if not filepath.exists():
        return False
        
    # Skip removal if it's part of core management tools
    if any(part in {"setuptools", "wheel", "pip"} for part in filepath.parts):
        return True
        
    try:
        filepath.unlink()
        return True
    except OSError as e:
        print(f"Error removing {filepath}: {e}")
        return False


def main() -> None:
    """
    Main function to clean and compile Python directories.
    """
    base_dir = "/data/data/com.termux/files/usr/lib/python3.12"
    if not Path(base_dir).exists():
        print(f"Directory {base_dir} does not exist. Skipping.")
        return

    print(f"Starting cleanup and compilation in {base_dir}...")

    # We use a set of strings for faster lookup
    excluded_names: Set[str] = {"site-packages", "__pycache__", "test"}

    for root, dirs, files in os.walk(base_dir):
        # 1. Remove .pyc files
        for file in files:
            if file.endswith(".pyc"):
                remove_pyc_file(os.path.join(root, file))

        # 2. Compile non-excluded directories
        # Create a list of directories to iterate over because we might modify 'dirs'
        for d in list(dirs):
            full_dp = os.path.join(root, d)
            
            # Check if directory or its path contains any excluded names
            if any(ex in d or ex in full_dp for ex in excluded_names):
                continue
            
            print(f"Compiling: {full_dp}")
            try:
                compileall.compile_dir(full_dp, quiet=1)
            except Exception as e:
                print(f"Failed to compile {full_dp}: {e}")


if __name__ == "__main__":
    main()
