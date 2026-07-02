#!/usr/bin/env python3
"""Recursively identifies and deletes broken symbolic links.

This script scans the current directory and all subdirectories for symbolic
links. If a link's target does not exist, the script deletes the broken link.
"""

import os
import sys
from pathlib import Path


def delete_broken_links(root_dir: Path) -> None:
    """Recursively deletes broken symbolic links starting from root_dir.

    Args:
        root_dir: Path object representing the starting directory.
    """
    deleted_count = 0
    for path in root_dir.rglob("*"):
        if path.is_symlink():
            # Check if the target exists
            if not path.exists():
                try:
                    path.unlink()
                    print(f"Deleted broken link: {path}")
                    deleted_count += 1
                except OSError as e:
                    print(f"Error deleting {path}: {e}")
    
    print(f"Total broken links deleted: {deleted_count}")


def main() -> None:
    """Main execution function to delete broken symbolic links."""
    current_dir = Path.cwd()
    delete_broken_links(current_dir)


if __name__ == "__main__":
    main()
