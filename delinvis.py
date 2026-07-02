#!/data/data/com.termux/files/usr/bin/env python3
"""
A utility to identify and remove unprintable (invisible) characters from text files.
This script scans a file for characters not in string.printable (excluding \n, \r, \t)
and creates a cleaned version of the file.
"""

import os
import shutil
import string
import sys


def find_unprintable_positions(text):
    """
    Identifies the line and column positions of all unprintable characters in the text.

    Args:
        text (str): The text content to scan.

    Returns:
        list: A list of tuples containing (line_num, col_num, char, ord_code).
    """
    allowed = set(string.printable) | {"\n", "\r", "\t"}
    positions = []

    line_num = 1
    col_num = 1
    for ch in text:
        if ch not in allowed:
            positions.append((line_num, col_num, ch, ord(ch)))
        if ch == "\n":
            line_num += 1
            col_num = 1
        else:
            col_num += 1
    return positions


def clean_text(text):
    """
    Removes all characters from the text that are not in string.printable (plus whitespace).

    Args:
        text (str): The text content to clean.

    Returns:
        str: The cleaned text content.
    """
    allowed = set(string.printable) | {"\n", "\r", "\t"}
    # Using a translation table for potentially better performance on large strings
    return "".join(ch for ch in text if ch in allowed)


def clean_file(path: str) -> None:
    """
    Reads a file, identifies unprintable characters, and overwrites it with a cleaned version.
    A backup file (.bak) is created before modification.

    Args:
        path (str): The absolute or relative path to the file.
    """
    backup_path = path + ".bak"
    try:
        shutil.copy2(path, backup_path)
    except OSError as e:
        print(f"Warning: Could not create backup file: {e}")

    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            data = f.read()
    except OSError as e:
        print(f"Error: Could not read file '{path}': {e}")
        return

    positions = find_unprintable_positions(data)
    if positions:
        print(f"Found {len(positions)} unprintable character(s) in '{path}':")
        for line, col, ch, code in positions:
            print(f"  Line {line}, Col {col}: char code {code} (0x{code:02X})")
        
        cleaned = clean_text(data)
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(cleaned)
            print(f"Successfully cleaned '{path}'. Backup saved as '{backup_path}'.")
        except OSError as e:
            print(f"Error: Could not write cleaned data to '{path}': {e}")
    else:
        print(f"No unprintable characters found in '{path}'.")


def main():
    """
    Main entry point for the delinvis script.
    """
    if len(sys.argv) != 2:
        print(f"Usage: {os.path.basename(sys.argv[0])} <filename>")
        sys.exit(1)

    fname = sys.argv[1]
    if not os.path.isfile(fname):
        print(f"Error: '{fname}' is not a file")
        sys.exit(1)

    clean_file(fname)


if __name__ == "__main__":
    main()
