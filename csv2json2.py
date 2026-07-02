#!/usr/bin/env python3
"""
Converts a CSV file to a JSON file as a list of dictionaries.
Each row in the CSV becomes a dictionary with keys from the header.
"""

import csv
import json
import sys
from pathlib import Path


def csv_to_json(csv_file_path: str) -> None:
    """
    Reads a CSV file and writes its content to a JSON file.

    Args:
        csv_file_path: Path to the input CSV file.
    """
    csv_path = Path(csv_file_path)

    if not csv_path.is_file():
        print(f"Error: file not found or is not a file: {csv_path}")
        sys.exit(1)

    json_path = csv_path.with_suffix(".json")

    try:
        with csv_path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            data = list(reader)

        if not data:
            print(f"Warning: {csv_path} is empty or has no data rows.")

        with json_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False, sort_keys=True)

        print(f"Successfully converted: {csv_path} → {json_path}")
    except Exception as e:
        print(f"Error during conversion: {e}")
        sys.exit(1)


def main() -> None:
    """
    Main entry point. Expects one argument: the CSV file path.
    """
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <file.csv>")
        sys.exit(1)

    csv_to_json(sys.argv[1])


if __name__ == "__main__":
    main()
