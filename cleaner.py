#!/usr/bin/env python3
"""Cleans terminal transcript files by removing ANSI and tmux artifacts.

This script processes a text file (e.g., a tmux transcript) and removes
ANSI escape sequences and tmux-specific status line artifacts while
preserving the overall line structure and newlines.
"""

import re
import sys
from pathlib import Path


def clean_terminal_transcript(file_path: Path) -> None:
    """Removes ANSI escape sequences and tmux artifacts from a file.

    Args:
        file_path: Path object to the transcript file to be cleaned.
    """
    # Comprehensive ANSI + tmux escape sequences
    ansi_tmux_re = re.compile(
        rb"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])|"
        rb"\x08|\x0C|\x0F|\x18|\x1C|"
        rb"\(\d+[a-z]\(B|\(0[Bqtxl]\(B"
    )

    # Tmux status lines / artifacts
    status_re = re.compile(
        rb"\b\d{4}[MGB]\b|"
        rb"\d{3,4}\s+\([^\)]+\)|"
        rb"\[\^\]\(B\(0l\(B<\(0q\(B\s*\d+|"
        rb"\~\\/[^\r\n]*?\s+\$|"
        rb"\(0mqq\(B\s+\d+M\s*/\s*\d+G"
    )

    try:
        content = file_path.read_bytes()

        # Remove status lines first
        content = status_re.sub(b"", content)

        # Remove ANSI/tmux sequences
        content = ansi_tmux_re.sub(b"", content)

        # Decode preserving newlines
        text = content.decode("utf-8", errors="replace")

        # Keep ALL newlines, tabs, spaces - remove only destructive controls
        cleaned_lines = []
        for line in text.splitlines(keepends=True):
            # Remove specific destructive controls from each line
            cleaned_line = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", line)
            cleaned_lines.append(cleaned_line)

        result = "".join(cleaned_lines)

        file_path.write_text(result, encoding="utf-8")
        print(f"✓ Cleaned (newlines preserved): {file_path.name}")

    except (OSError, UnicodeDecodeError) as e:
        print(f"✗ Error processing '{file_path.name}': {e}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    """Main execution function to handle command-line arguments."""
    if len(sys.argv) != 2:
        print(f"Usage: {Path(sys.argv[0]).name} <transcript_file>")
        sys.exit(1)

    fname = Path(sys.argv[1])
    if not fname.is_file():
        print(f"Error: '{fname}' not found or is not a file.")
        sys.exit(1)

    clean_terminal_transcript(fname)


if __name__ == "__main__":
    main()
