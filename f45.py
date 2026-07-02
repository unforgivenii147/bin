#!/usr/bin/env python3
"""
A utility to fold text file content to a specific width (default 45 characters).
Can either cut strictly at the width or try to break at spaces (smart folding).
"""

import os
import sys
import tempfile
from pathlib import Path


def fold_text(text: str, width: int = 45, smart_break: bool = True) -> str:
    """
    Folds text to a specific width.
    
    Args:
        text (str): The input text to fold.
        width (int): Maximum line width.
        smart_break (bool): If True, attempts to break lines at spaces.
        
    Returns:
        str: The folded text.
    """
    lines = text.splitlines()
    folded_lines = []

    for line in lines:
        if not line:
            folded_lines.append("")
            continue
            
        while len(line) > width:
            if smart_break:
                # Find the last space within the width
                break_point = line.rfind(" ", 0, width + 1)
                if break_point == -1:
                    # No space found, forced cut at width
                    break_point = width
            else:
                break_point = width
            
            folded_lines.append(line[:break_point].rstrip())
            line = line[break_point:].lstrip()
            
        if line:
            folded_lines.append(line)

    return "\n".join(folded_lines) + "\n"


def fold_file_inplace(filename: str, width: int = 45) -> None:
    """
    Folds the content of a file in-place.
    
    Args:
        filename (str): Path to the file to fold.
        width (int): Target width for folding.
    """
    path = Path(filename)
    if not path.exists():
        print(f"Error: File '{filename}' not found.", file=sys.stderr)
        return

    try:
        # Read content
        original_content = path.read_text(encoding="utf-8", errors="ignore")
        
        # Fold content
        folded_content = fold_text(original_content, width=width, smart_break=True)
        
        # Write back to file safely using a temporary file
        fd, temp_path = tempfile.mkstemp(dir=path.parent, text=True)
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(folded_content)
        
        # Replace original file with temporary file
        os.replace(temp_path, filename)
        print(f"Successfully folded '{filename}' to {width} columns.")
        
    except Exception as e:
        print(f"Error processing '{filename}': {e}", file=sys.stderr)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {os.path.basename(sys.argv[0])} <filename> [width]", file=sys.stderr)
        sys.exit(1)
        
    file_to_fold = sys.argv[1]
    target_width = int(sys.argv[2]) if len(sys.argv) > 2 else 45
    
    fold_file_inplace(file_to_fold, target_width)
