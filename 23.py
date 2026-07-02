#!/usr/bin/env python3
"""Recursively lint and format Python files using Ruff.

This script identifies Python files (by extension or shebang) in the current
directory and its subdirectories, then applies linting fixes and formatting
using the Ruff tool in parallel.
"""

import os
import subprocess
import sys
from multiprocessing import Lock, Pool, cpu_count
from pathlib import Path
from typing import List, Tuple

# Global lock for printing to avoid interleaved output from processes
print_lock = Lock()


def is_python_file(path: Path) -> bool:
    """Determines if a file is a Python file.

    Criteria: Ends in .py OR has a python shebang.

    Args:
        path: Path object to the file.

    Returns:
        True if the file is identified as Python, False otherwise.
    """
    if path.suffix == ".py":
        return True

    # Check for extensionless executable python scripts
    if path.suffix == "" and path.is_file():
        try:
            # Read only the first 64 bytes to check shebang
            with open(path, "rb") as f:
                head = f.read(64)
                # Look for standard shebangs
                if b"python" in head and b"#!" in head:
                    return True
        except (OSError, PermissionError):
            return False
    return False


def run_command(cmd: List[str]) -> Tuple[int, str, str]:
    """Runs a subprocess command and returns its results.

    Args:
        cmd: The command to run as a list of strings.

    Returns:
        A tuple of (returncode, stdout, stderr).
    """
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, encoding="utf-8", check=False
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, "", str(e)


def process_file(file_path_str: str) -> None:
    """Worker function to lint and format a single file.

    1. Run ruff check (fixes)
    2. Run ruff format (styling)

    Args:
        file_path_str: String path to the file.
    """
    path = Path(file_path_str)

    # --- Step 1: Apply Fixes (Linter) ---
    check_cmd = [
        "ruff",
        "check",
        "--fix",
        "--unsafe-fixes",
        "--line-length",
        "79",
        "--quiet",
        str(path),
    ]

    rc_check, out_check, err_check = run_command(check_cmd)

    # --- Step 2: Apply Formatting (Styler) ---
    format_cmd = [
        "ruff",
        "format",
        "--line-length",
        "79",
        str(path),
    ]

    # Try to find a local config if available, otherwise use defaults
    config_path = Path("/data/data/com.termux/files/home/.config/ruff/ruff.toml")
    if config_path.exists():
        format_cmd.extend(["--config", str(config_path)])

    rc_fmt, out_fmt, err_fmt = run_command(format_cmd)

    output = []
    if rc_check != 0 or err_check.strip():
        output.append(f"--- Issues fixing {path.name} ---")
        if err_check.strip():
            output.append(err_check.strip())
        if out_check.strip():
            output.append(out_check.strip())

    if rc_fmt != 0 or err_fmt.strip():
        output.append(f"--- Issues formatting {path.name} ---")
        if err_fmt.strip():
            output.append(err_fmt.strip())

    if output:
        with print_lock:
            print("\n".join(output))
            sys.stdout.flush()


def get_all_files(root_dir: str) -> List[str]:
    """Recursively finds all Python files while skipping ignored directories.

    Args:
        root_dir: The root directory to start searching from.

    Returns:
        A list of string paths to Python files.
    """
    py_files = []
    ignore_dirs = {
        ".git", ".venv", "venv", "__pycache__", "build", "dist", "node_modules"
    }
    for root, dirs, files in os.walk(root_dir):
        # Modifying dirs in-place to skip ignored directories
        dirs[:] = [d for d in dirs if d not in ignore_dirs]

        for file in files:
            file_path = Path(root) / file
            if is_python_file(file_path):
                py_files.append(str(file_path))
    return py_files


def main() -> None:
    """Main function to coordinate linting and formatting of all Python files."""
    try:
        subprocess.run(
            ["ruff", "--version"], capture_output=True, check=True
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("Error: 'ruff' is not installed or not in PATH.")
        print("Please run: pip install ruff")
        sys.exit(1)

    root_dir = os.getcwd()
    files = get_all_files(root_dir)

    if not files:
        return

    num_procs = min(len(files), cpu_count())

    with Pool(num_procs) as pool:
        pool.map(process_file, files)


if __name__ == "__main__":
    main()
