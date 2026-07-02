#!/data/data/com.termux/files/usr/bin/python
"""
Clean non-printing characters from a text file.

This module removes control characters and other non-printing characters
from a file while preserving common whitespace like newlines and tabs.
"""

import sys
import unicodedata
from pathlib import Path


def clean_file(filename: str) -> None:
    """
    Remove non-printing characters from the specified file in-place.

    Args:
        filename: The path to the file to be cleaned.
    """
    path = Path(filename)
    try:
        if not path.is_file():
            print(f"Error: The file '{filename}' was not found.")
            return

        # Read the original file
        content = path.read_text(encoding="utf-8")

        # unicodedata.category(c) 'C' stands for 'Other' (Control, Private Use, etc.)
        # This removes non-printing characters but keeps standard spaces and newlines
        cleaned_content = "".join(
            ch for ch in content 
            if unicodedata.category(ch)[0] != "C" or ch in "\n\r\t"
        )

        # Overwrite the file with the cleaned version
        path.write_text(cleaned_content, encoding="utf-8")

        print(f"Successfully cleaned: {filename}")

    except Exception as e:
        print(f"An error occurred while processing '{filename}': {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <filename>")
    else:
        target_file = sys.argv[1]
        clean_file(target_file)
