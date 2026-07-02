#!/usr/bin/env python3
"""
Recursively searches for a specific string (default: 'b64 = """') in all files
within the current directory and its subdirectories.
"""

import os
import sys


def search_in_files(search_string: str, directory: str = ".") -> None:
    """
    Recursively walks through the directory and prints paths of files
    containing the search_string. Reads files line by line for memory efficiency.
    """
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    for line in f:
                        if search_string in line:
                            print(f"Found in file: {file_path}")
                            break
            except (UnicodeDecodeError, PermissionError, OSError):
                # Skip binary files, files with encoding issues, or unreadable files
                continue


def main() -> None:
    """
    Main entry point. Parses command line arguments or uses default search string.
    """
    search_string = sys.argv[1] if len(sys.argv) > 1 else 'b64 = """'
    search_in_files(search_string)


if __name__ == "__main__":
    main()
