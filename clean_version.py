#!/data/data/com.termux/files/usr/bin/env python3
"""
Extract package names from a pip freeze output file and overwrite it.

This module provides a command-line utility to strip version information
from a requirements file, leaving only the package names.
"""

import argparse
from typing import Optional
import regex as re
from pathlib import Path

# Regular expression to match package names, including optional editable flags
PKG_NAME_RE = re.compile(
    r"""
    ^\s*
    (?:
        -e\s+                # editable install
    )?
    (?P<name>[A-Za-z0-9_.\-]+)
    """,
    re.VERBOSE,
)


def extract_package_name(line: str) -> Optional[str]:
    """
    Extract the package name from a single line of pip freeze output.

    Args:
        line: A line of text from pip freeze.

    Returns:
        The extracted package name, or None if no name could be found.
    """
    line = line.strip()

    # Skip empty lines and comments
    if not line or line.startswith("#"):
        return None

    # Skip direct references without a clear package name
    if line.startswith(("git+", "http://", "https://")):
        return None

    # Handle PEP 508 direct refs: pkg @ url
    if "@" in line:
        name = line.split("@", 1)[0].strip()
        return name if name else None

    # Handle normal cases: pkg==1.2.3, pkg>=1.0, etc.
    match = PKG_NAME_RE.match(line)
    if match:
        return match.group("name")

    return None


def main() -> None:
    """
    Main execution function for the script.
    """
    parser = argparse.ArgumentParser(
        description="Clean pip freeze output and keep only package names (overwrite file)."
    )
    parser.add_argument("file", help="Path to the pip freeze output file to clean")
    args = parser.parse_args()

    path = Path(args.file)

    if not path.is_file():
        print(f"Error: file not found: {path}")
        return

    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
        lines = content.splitlines()
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    packages = []
    for line in lines:
        name = extract_package_name(line)
        if name:
            packages.append(name)

    # Deduplicate while preserving order
    seen = set()
    cleaned = [p for p in packages if not (p in seen or seen.add(p))]

    try:
        path.write_text("\n".join(cleaned) + "\n", encoding="utf-8")
        print(f"Successfully cleaned '{path}' and kept {len(cleaned)} packages.")
    except Exception as e:
        print(f"Error writing file: {e}")


if __name__ == "__main__":
    main()
