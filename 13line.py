#!/usr/bin/env python3
"""Extract first 13 lines of all source files recursively.

This script scans the current directory for files with specific extensions,
extracts the first 13 lines of each, deduplicates the snippets, and writes
the unique snippets to 'all.txt' with 3 blank lines between them.
"""

import os
from pathlib import Path
from typing import List, Set

EXTENSIONS = {
    ".py", ".h", ".c", ".cpp", ".cc", ".cxx", ".hh", ".hpp", ".hxx"
}


def get_first_13(path: Path) -> str:
    """Reads the first 13 lines of a file.

    Args:
        path: The path to the file to read.

    Returns:
        A string containing the first 13 lines of the file.
    """
    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            lines = [f.readline() for _ in range(13)]
        return "".join(line for line in lines if line)
    except (OSError, UnicodeDecodeError):
        return ""


def main() -> None:
    """Main execution function to collect and save unique file snippets."""
    output_path = Path("all.txt").resolve()
    collected: Set[str] = set()

    for path in Path.cwd().rglob("*"):
        if not path.is_file():
            continue

        if path.suffix not in EXTENSIONS:
            continue

        # Prevent including output file itself
        if path.resolve() == output_path:
            continue

        snippet = get_first_13(path)
        if snippet.strip():
            collected.add(snippet)

    unique_collected: List[str] = sorted(list(collected))

    with open(output_path, "w", encoding="utf-8") as out:
        for snippet in unique_collected:
            out.write(snippet)
            # Ensure snippet ends with newline before adding extra ones
            if not snippet.endswith("\n"):
                out.write("\n")
            out.write("\n\n\n")

    print(f"Unique snippets saved → {output_path}")
    print(f"Total unique blocks: {len(unique_collected)}")


if __name__ == "__main__":
    main()
