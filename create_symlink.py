#!/data/data/com.termux/files/usr/bin/python
"""
Creates symlinks for Python scripts in a directory, removing the .py extension.
This allows running the scripts by their base name if the directory is in the PATH.
"""

import os
import sys
from pathlib import Path


def create_symlinks(directory: str) -> None:
    """
    Iterates through .py files in the given directory and creates extension-less symlinks.

    Args:
        directory: The path to the directory containing Python scripts.
    """
    source_dir = Path(directory).expanduser().resolve()

    if not source_dir.is_dir():
        print(f"Error: {source_dir} is not a directory.")
        return

    # Get the current script's path to avoid symlinking itself
    current_script = Path(__file__).resolve()

    for file_path in source_dir.glob("*.py"):
        if not file_path.is_file() or file_path == current_script:
            continue

        # Create symlink name by removing .py extension
        link_path = file_path.with_suffix("")

        try:
            # Using relative symlink can sometimes be more portable
            # But absolute is safer for local bin directories
            os.symlink(file_path, link_path)
            print(f"Created symlink: {link_path.name} -> {file_path.name}")
        except FileExistsError:
            # If it exists but points elsewhere, we might want to update it,
            # but for now, just skip as per original logic.
            print(f"Symlink already exists: {link_path.name}")
        except Exception as e:
            print(f"Error creating symlink for {file_path.name}: {e}")


def main() -> None:
    """
    Main entry point. Defaults to ~/bin if no argument is provided.
    """
    target_dir = sys.argv[1] if len(sys.argv) > 1 else "~/bin"
    create_symlinks(target_dir)


if __name__ == "__main__":
    main()
