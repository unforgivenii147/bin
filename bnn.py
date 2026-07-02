#!/usr/bin/env python3
"""Replaces literal backslash-n sequences with actual newlines in a file.

This script is useful for fixing files where newlines have been escaped as
the string '\\n' instead of being interpreted as line breaks.
"""

import sys
from pathlib import Path


def fix_escaped_newlines(file_path: Path) -> None:
    """Replaces literal '\\n' with actual newline characters in a file.

    Args:
        file_path: Path object to the file to be fixed.
    """
    if not file_path.is_file():
        print(f"Error: '{file_path}' is not a valid file.")
        return

    try:
        content = file_path.read_text(encoding="utf-8")
        if "\\n" not in content:
            print(f"No escaped newlines found in '{file_path.name}'.")
            return

        fixed_content = content.replace("\\n", "\n")
        file_path.write_text(fixed_content, encoding="utf-8")
        print(f"Successfully fixed escaped newlines in '{file_path.name}'.")
    except (OSError, UnicodeDecodeError) as e:
        print(f"Error processing '{file_path.name}': {e}")


def main() -> None:
    """Main execution function to handle command-line arguments."""
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <filename>")
        sys.exit(1)

    fname = Path(sys.argv[1])
    fix_escaped_newlines(fname)


if __name__ == "__main__":
    main()
