#!/usr/bin/env python3
"""
python_formatter.py
Requirements: pip install yapf black autopep8 isort autoflake
"""

from __future__ import annotations

import argparse
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

# Standard library imports remain at top
IGNORED_DIRS = {
    '.git', 'dist', 'build', '__pycache__', '.venv', 'node_modules'
}

# ---------- UTILS ----------


def is_python_file(path: Path) -> bool:
    if path.suffix in {'.py', '.pyi', '.pyx'}:
        return True
    try:
        with path.open('rb') as f:
            line = f.readline(100)
            return line.startswith(b'#!') and b'python' in line.lower()
    except Exception:
        return False


# ---------- FORMATTING LOGIC ----------


def format_single_file(file: Path, args) -> bool:
    print(f'processing {file.name}')
    """Core formatting logic using Lazy Imports."""
    try:
        original_code = file.read_text(encoding='utf-8')
        code = original_code

        # 1. Remove Unused Imports/Variables
        if args.remove_all_unused_imports:
            import autoflake
            code = autoflake.fix_code(code,
                                      remove_all_unused_imports=True,
                                      remove_unused_variables=True)

        # 2. Sort Imports
        if args.isort:
            import isort
            code = isort.code(code)

        # 3. Code Style Formatting
        if args.black:
            import black
            try:
                code = black.format_str(code, mode=black.Mode())
            except black.NothingChanged:
                pass
        elif args.autopep:
            import autopep8
            code = autopep8.fix_code(code, options={'aggressive': 2})
        else:
            # Lazy import for yapf
            from yapf.yapflib import yapf_api
            code, _ = yapf_api.FormatCode(code)

        # 4. Write back only if changed
        if code != original_code:
            file.write_text(code, encoding='utf-8')
            return True
        return False
    except Exception as e:
        print(f"Error processing {file.name}: {e}")
        return False


# ---------- EXECUTION ----------


def main() -> None:
    p = argparse.ArgumentParser(
        description='Fast Python API-based formatter (Lazy Loading)')
    p.add_argument('files',
                   nargs='*',
                   help='Specific files to format (optional)')
    p.add_argument('-b',
                   '--black',
                   action='store_true',
                   help='Use black style')
    p.add_argument('-a',
                   '--autopep',
                   action='store_true',
                   help='Use autopep8 style')
    p.add_argument('-i', '--isort', action='store_true', help='Sort imports')
    p.add_argument('-r',
                   '--remove-all-unused-imports',
                   action='store_true',
                   help='Autoflake cleanup')
    p.add_argument('-t',
                   '--time',
                   action='store_true',
                   help='Show overall runtime')
    args = p.parse_args()

    start_time = time.perf_counter()

    # Step 1: Collect Files
    if args.files:
        files = [
            Path(f) for f in args.files
            if Path(f).is_file() and is_python_file(Path(f))
        ]
    else:
        files = [
            f for f in Path('.').rglob('*') if f.is_file() and not any(
                part in IGNORED_DIRS for part in f.parts) and is_python_file(f)
        ]

    if not files:
        print('No Python files detected.')
        return

    print(f"Formatting {len(files)} files...")

    # Step 2: Parallel Execution
    # map handles the distribution; lambda passes the context
    with ThreadPoolExecutor(max_workers=8) as executor:
        results = list(
            executor.map(lambda f: format_single_file(f, args), files))

    # Step 3: Reporting
    changed_count = sum(1 for r in results if r)
    print(f"Done. {changed_count} files modified.")

    if args.time:
        duration = time.perf_counter() - start_time
        print(f"Total Runtime: {duration:.4f} seconds")


if __name__ == '__main__':
    main()
