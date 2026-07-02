#!/data/data/com.termux/files/usr/bin/env python3
"""
Clean and sort Python requirements files.

This module provides functionality to extract package names from requirements.txt
files, removing version constraints, extras, and comments, and then sorting
them in a grouped manner.
"""

import sys
from typing import List, Set, Tuple

import regex as re
from pathlib import Path

# Pattern to split on version operators
_VERSION_OP_RE = re.compile(r"\s*(?:===|==|!=|>=|<=|~=|>|<)\s*")


def clean_requirement(line: str) -> str:
    """
    Extract the base package name from a requirement line.

    Args:
        line: A line from a requirements file.

    Returns:
        The cleaned package name, or an empty string if the line is empty or a comment.
    """
    # Remove comments
    line = line.split("#", 1)[0].strip()
    if not line:
        return ""

    # Remove environment markers ("; something")
    line = line.split(";", 1)[0].strip()
    if not line:
        return ""

    # Remove extras like pkg[extra]
    line = re.sub(r"\[.*?\]", "", line).strip()
    if not line:
        return ""

    # Remove version operators
    parts = _VERSION_OP_RE.split(line, maxsplit=1)
    name = parts[0].strip()

    return name


def group_key(name: str) -> Tuple[int, str]:
    """
    Create a sort key for grouping and sorting package names.

    Groups by first character class:
    0 = Uppercase
    1 = Lowercase
    2 = Other
    Sorts case-sensitively within group.

    Args:
        name: The package name.

    Returns:
        A tuple representing the sort order.
    """
    if not name:
        return (2, name)
    first = name[0]
    if first.isupper():
        return (0, name)
    elif first.islower():
        return (1, name)
    else:
        return (2, name)


def main() -> None:
    """
    Main entry point for the script. Parses arguments and processes the file.
    """
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} requirements.txt", file=sys.stderr)
        sys.exit(1)

    fname = sys.argv[1]
    path = Path(fname)

    if not path.is_file():
        print(f"Error: File '{fname}' not found.", file=sys.stderr)
        sys.exit(1)

    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)

    cleaned: List[str] = []
    seen: Set[str] = set()
    for line in lines:
        c = clean_requirement(line)
        if c and c not in seen:
            cleaned.append(c)
            seen.add(c)

    # Grouped + case-sensitive sorted
    cleaned = sorted(cleaned, key=group_key)

    # Write back in-place
    try:
        path.write_text("\n".join(cleaned) + "\n", encoding="utf-8")
    except Exception as e:
        print(f"Error writing file: {e}", file=sys.stderr)
        sys.exit(1)

    # Print output file contents
    print("\n=== Cleaned Requirements ===")
    for item in cleaned:
        print(item)


if __name__ == "__main__":
    main()
