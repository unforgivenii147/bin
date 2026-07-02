#!/usr/bin/env python3
"""
Converts a two-column CSV file into a JSON flat mapping.
The first column is used as the key and the second column as the value.
"""

import csv
import json
import sys
from pathlib import Path


def csv_to_json_map(csv_file_path: str) -> None:
    """
    Reads a CSV and creates a JSON object where the first column maps to the second.

    Args:
        csv_file_path: Path to the input CSV file.
    """
    csv_path = Path(csv_file_path)

    if not csv_path.is_file():
        print(f"Error: file not found or is not a file: {csv_path}")
        sys.exit(1)

    json_path = csv_path.with_suffix(".json")
    result = {}

    try:
        with csv_path.open(newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader, None)  # skip header

            if header is None:
                print(f"Error: {csv_path} is empty")
                sys.exit(1)

            if len(header) < 2:
                print("Error: CSV must have at least two columns to create a mapping")
                sys.exit(1)

            for row in reader:
                if len(row) < 2:
                    continue  # skip malformed rows

                key = row[0].strip()
                value = row[1].strip()

                if key:
                    result[key] = value

        with json_path.open("w", encoding="utf-8") as f:
            json.dump(result, f, indent=4, ensure_ascii=False, sort_keys=True)

        print(f"Successfully converted (mapping): {csv_path} → {json_path}")
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

    csv_to_json_map(sys.argv[1])


if __name__ == "__main__":
    main()
