#!/usr/bin/env python3
"""Inserts author metadata header into Python files.

This script scans the current directory for Python files (detected by extension
or content) and prepends a metadata header containing the author's name, email,
and the current timestamp.
"""

import datetime
import json
import os
import sys
from pathlib import Path
from typing import Dict, Optional

INFO_PATH = Path("~/.info.json").expanduser()


def load_user_info() -> Dict[str, str]:
    """Loads user metadata from a JSON file.

    Returns:
        A dictionary containing user info, or default values if the file
        is missing or invalid.
    """
    if not INFO_PATH.exists():
        # Fallback to environment variables or defaults
        return {
            "name": os.getenv("USER", "Unknown Author"),
            "email": os.getenv("EMAIL", "unknown@example.com")
        }

    try:
        with INFO_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {"name": "Unknown Author", "email": "unknown@example.com"}


def is_python_file(path: Path) -> bool:
    """Detects if a file is a Python file.

    Criteria: .py extension OR has a python shebang OR contains python keywords.

    Args:
        path: Path object to the file.

    Returns:
        True if the file is identified as Python, False otherwise.
    """
    if not path.is_file():
        return False

    if path.suffix == ".py":
        return True

    try:
        with path.open("r", encoding="utf-8", errors="ignore") as f:
            first_line = f.readline().strip()
            if first_line.startswith("#!"):
                return "python" in first_line

            # Sample further for keywords
            content = f.read(512)
            keywords = {"def ", "class ", "import ", "from "}
            return any(kw in content for kw in keywords)
    except OSError:
        return False


def build_header(info: Dict[str, str]) -> str:
    """Constructs the metadata header string.

    Args:
        info: A dictionary containing 'name' and 'email'.

    Returns:
        A formatted header string.
    """
    now = datetime.datetime.now()
    timestamp = now.strftime("%a %d %b %Y | %H:%M:%S")
    name = info.get("name", "Unknown Author")
    email = info.get("email", "unknown@example.com")
    return f"# Author : {name}\n# Email  : {email}\n# Time   : {timestamp}\n\n\n"


def has_header(content: str) -> bool:
    """Checks if the file content already contains an author header.

    Args:
        content: The content of the file.

    Returns:
        True if a header is detected in the first few lines.
    """
    lines = content.splitlines()[:5]
    return any("# Author :" in line for line in lines)


def process_file(path: Path, header: str) -> None:
    """Prepends the header to the file if it's missing.

    Args:
        path: Path object to the file.
        header: The header string to prepend.
    """
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        if has_header(content):
            return

        # Handle shebang preservation
        if content.startswith("#!"):
            parts = content.split("\n", 1)
            if len(parts) > 1:
                new_content = f"{parts[0]}\n{header}{parts[1]}"
            else:
                new_content = f"{content}\n{header}"
        else:
            new_content = f"{header}{content}"

        with path.open("w", encoding="utf-8") as f:
            f.write(new_content)
    except OSError as e:
        print(f"Error processing {path}: {e}")


def main() -> None:
    """Main execution function to scan and update files."""
    info = load_user_info()
    header = build_header(info)

    for path in Path(".").rglob("*"):
        if is_python_file(path):
            process_file(path, header)


if __name__ == "__main__":
    main()
