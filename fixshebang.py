#!/usr/bin/env python3
"""
Recursively updates Python shebang lines in .py files.
By default, it converts shebangs to the Termux-compatible format.
"""

import re
import sys
import argparse
from pathlib import Path

TERMUX_SHEBANG = "#!/data/data/com.termux/files/usr/bin/env python3"
STANDARD_SHEBANG = "#!/usr/bin/env python3"
SHEBANG_RE = re.compile(r"^#!.*python[0-9.]*.*$")


def fix_file(path: Path, new_shebang: str) -> bool:
    """
    Checks if a file has a Python shebang and updates it if it differs from new_shebang.
    """
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return False

    lines = text.splitlines()
    if not lines:
        return False

    if SHEBANG_RE.match(lines[0]):
        if lines[0] == new_shebang:
            return False

        lines[0] = new_shebang
        try:
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return True
        except OSError:
            print(f"Error writing to {path}")
            return False

    return False


def main() -> None:
    """
    Main entry point. Parses arguments and updates shebangs in Python files.
    """
    parser = argparse.ArgumentParser(description="Update Python shebang lines recursively.")
    parser.add_argument("directory", nargs="?", default=".", help="Directory to process (default: current)")
    parser.add_argument("--standard", action="store_true", help="Use standard shebang instead of Termux one")
    parser.add_argument("--custom", help="Use a custom shebang string")

    args = parser.parse_args()

    if args.custom:
        target_shebang = args.custom
    elif args.standard:
        target_shebang = STANDARD_SHEBANG
    else:
        target_shebang = TERMUX_SHEBANG

    root_dir = Path(args.directory)
    if not root_dir.is_dir():
        print(f"Error: {root_dir} is not a directory.")
        sys.exit(1)

    print(f"Updating Python shebangs to: {target_shebang}")
    fixed_count = 0
    for file in root_dir.rglob("*.py"):
        if fix_file(file, target_shebang):
            fixed_count += 1
            print(f"Updated: {file}")

    print(f"\nDone. Updated {fixed_count} files.")


if __name__ == "__main__":
    main()
