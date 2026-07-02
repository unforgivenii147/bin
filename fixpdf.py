#!/usr/bin/env python3
"""
Attempts to "fix" a PDF file by reading and re-writing it using pypdf.
This can often resolve minor structural issues or metadata corruption.
"""

import sys
import argparse
from pathlib import Path

try:
    from pypdf import PdfReader, PdfWriter
except ImportError:
    print("Error: 'pypdf' is required. Install it with 'pip install pypdf'.")
    sys.exit(1)


def fix_pdf(input_path: str, output_path: str) -> bool:
    """
    Reads a PDF file and writes it to a new location.
    Returns True if successful, False otherwise.
    """
    try:
        reader = PdfReader(input_path, strict=False)
        writer = PdfWriter()

        for page in reader.pages:
            writer.add_page(page)

        # Copy metadata if possible
        writer.add_metadata(reader.metadata)

        with open(output_path, "wb") as f:
            writer.write(f)
        
        return True
    except Exception as e:
        print(f"Error fixing PDF: {e}")
        return False


def main() -> None:
    """
    Main entry point. Parses command line arguments and initiates PDF fix.
    """
    parser = argparse.ArgumentParser(description="Fix minor PDF corruption by re-writing it.")
    parser.add_argument("input", help="Input PDF file path")
    parser.add_argument("output", nargs="?", help="Output PDF file path (default: fixed_[input])")

    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: File {input_path} not found.")
        sys.exit(1)

    if args.output:
        output_path = Path(args.output)
    else:
        output_path = input_path.parent / f"fixed_{input_path.name}"

    print(f"Attempting to fix '{input_path}'...")
    if fix_pdf(str(input_path), str(output_path)):
        print(f"Successfully saved fixed PDF to '{output_path}'")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
