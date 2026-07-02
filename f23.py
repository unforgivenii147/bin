#!/data/data/com.termux/files/usr/bin/env python3
"""
A utility to migrate Python 2 code to Python 3.
Primarily focuses on converting print statements and common function names (xrange, raw_input).
"""

import argparse
import shutil
from pathlib import Path
from typing import Tuple

import regex as re

# --- Regex Patterns ---
PRINT_PATTERN = re.compile(r"^\s*print\s+(?!\()(.+)$")  # matches: print <expr>
PRINT_BARE_PATTERN = re.compile(r"^\s*print\s*$")      # matches: print
EXCEPT_PATTERN = re.compile(r"^\s*except\s+(\S+)\s*,\s*(\S+)\s*:")  # matches: except E, e:


def fix_py2_to_py3_common(line: str) -> Tuple[str, bool]:
    """
    Applies common Python 2 to Python 3 string replacements on a single line.
    
    Args:
        line (str): The input line of code.
        
    Returns:
        Tuple[str, bool]: A tuple containing the (modified_line, changed_flag).
    """
    original = line

    line = line.replace("xrange(", "range(")
    line = line.replace("raw_input(", "input(")

    # Fix except E, e: -> except E as e:
    m = EXCEPT_PATTERN.match(line.strip())
    if m:
        indent = line[: len(line) - len(line.lstrip())]
        exc_type, exc_var = m.group(1), m.group(2)
        line = f"{indent}except {exc_type} as {exc_var}:\n"

    return line, (line != original)


def fix_print_statements(line: str) -> Tuple[str, bool]:
    """
    Converts Python 2 print statements to Python 3 print() functions.
    
    Args:
        line (str): A single line of code.
        
    Returns:
        Tuple[str, bool]: A tuple containing the (modified_line, changed_flag).
    """
    stripped = line.strip()
    indent = line[: len(line) - len(line.lstrip())]

    # Handle bare print
    if PRINT_BARE_PATTERN.match(stripped):
        return f"{indent}print()\n", True

    # Handle print with expression
    m = PRINT_PATTERN.match(stripped)
    if m:
        expr = m.group(1)
        # Ensure we don't double-wrap if it's already a function call (rare with this regex but safe)
        return f"{indent}print({expr})\n", True

    return line, False


def apply_fixes(text: str, apply_all: bool) -> Tuple[str, bool]:
    """
    Applies migration fixes to the entire content of a file.
    
    Args:
        text (str): The full content of the file.
        apply_all (bool): Whether to apply all fixes or just print statement fixes.
        
    Returns:
        Tuple[str, bool]: The (modified_text, changed_flag).
    """
    lines = text.splitlines(True)
    new_lines = []
    overall_changed = False

    for line in lines:
        changed = False
        
        if apply_all:
            line, c1 = fix_py2_to_py3_common(line)
            changed = changed or c1
            
        line, c2 = fix_print_statements(line)
        changed = changed or c2

        new_lines.append(line)
        overall_changed = overall_changed or changed

    return "".join(new_lines), overall_changed


def process_file(path: Path, force: bool, apply_all: bool, changed_files: list, error_files: list) -> None:
    """
    Processes a single file, applying fixes and handling backups.
    
    Args:
        path (Path): Path to the file.
        force (bool): If True, overwrites without backup.
        apply_all (bool): If True, applies all Py2->Py3 fixes.
        changed_files (list): List to track paths of changed files.
        error_files (list): List to track files that caused errors.
    """
    try:
        original = path.read_text(encoding="utf-8")
        fixed, changed = apply_fixes(original, apply_all)

        if changed:
            if not force:
                backup_path = path.with_suffix(path.suffix + ".bak")
                shutil.copy2(path, backup_path)

            path.write_text(fixed, encoding="utf-8")
            changed_files.append(str(path))

    except Exception as e:
        error_files.append((str(path), str(e)))


def scan_and_fix(root: Path, force: bool, apply_all: bool) -> Tuple[list, list]:
    """
    Recursively scans and fixes all Python files in the root directory.
    
    Args:
        root (Path): The starting directory.
        force (bool): Whether to overwrite files.
        apply_all (bool): Whether to apply all migration fixes.
        
    Returns:
        Tuple[list, list]: (changed_files, error_files)
    """
    changed_files = []
    error_files = []
    for f in root.rglob("*.py"):
        process_file(f, force, apply_all, changed_files, error_files)
    return changed_files, error_files


def main():
    """
    Main entry point: parses CLI arguments and runs the migration scan.
    """
    parser = argparse.ArgumentParser(
        description="Fix Python 2 print statements and optionally apply common Py2->Py3 conversions."
    )
    parser.add_argument(
        "-f", "--force", action="store_true",
        help="Overwrite original files (no .bak backups)",
    )
    parser.add_argument("-a", "--all", action="store_true", help="Apply all Python 2 to Python 3 fixes")

    args = parser.parse_args()

    # Default behavior: if no arguments, be helpful but safe (or as previously defined)
    # The original script defaulted to force=True, all=True if no flags provided.
    if not any(vars(args).values()):
        args.force = True
        args.all = True

    root = Path(".").resolve()
    print(f"Scanning and fixing files in: {root}")
    
    changed, errors = scan_and_fix(root, force=args.force, apply_all=args.all)

    print("\n=== SUMMARY ===")
    print(f"Files changed: {len(changed)}")
    for f in sorted(changed):
        print(f"  - {f}")

    if errors:
        print(f"\nFiles with errors: {len(errors)}")
        for f, e in errors:
            print(f"  - {f}: {e}")


if __name__ == "__main__":
    main()
