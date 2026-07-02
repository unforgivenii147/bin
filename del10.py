#!/data/data/com.termux/files/usr/bin/env python3
"""
Filters a file by removing lines that are shorter than a specified length.
By default, it keeps lines with at least 30 characters of non-whitespace content.
"""

import sys
import os
from pathlib import Path


def filter_lines_by_length(file_path: str, min_length: int = 30) -> None:
    """
    Reads a file and overwrites it with lines that meet the minimum length requirement.

    Args:
        file_path: Path to the file to process.
        min_length: Minimum number of non-whitespace characters required to keep a line.
    """
    path = Path(file_path)
    if not path.is_file():
        print(f"Error: File '{file_path}' not found.")
        return

    temp_path = path.with_suffix(".tmp")
    
    try:
        count_before = 0
        count_after = 0
        
        with path.open("r", encoding="utf-8") as fin, \
             temp_path.open("w", encoding="utf-8") as fout:
            for line in fin:
                count_before += 1
                if len(line.strip()) >= min_length:
                    fout.write(line)
                    count_after += 1
        
        # Replace original file with the filtered one
        os.replace(temp_path, path)
        print(f"Processed {file_path}: Kept {count_after}/{count_before} lines (min length {min_length}).")
        
    except Exception as e:
        print(f"An error occurred while processing {file_path}: {e}")
        if temp_path.exists():
            temp_path.unlink()


def main() -> None:
    """
    Main entry point. Usage: del10.py <filename> [min_length]
    """
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <filename> [min_length]")
        sys.exit(1)

    fname = sys.argv[1]
    min_len = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    
    filter_lines_by_length(fname, min_len)


if __name__ == "__main__":
    main()
