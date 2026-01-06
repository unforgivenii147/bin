#!/data/data/com.termux/files/usr/bin/env python3

import os
import subprocess
import sys
from multiprocessing import Lock, Pool, cpu_count
from pathlib import Path

# Global lock for printing to avoid interleaved output from processes
print_lock = Lock()


def is_python_file(path: Path) -> bool:
    """Determines if a file is a Python file.
    Criteria: Ends in .py OR has a python shebang.
    """
    if path.suffix == '.py':
        return True

    # Check for extensionless executable python scripts
    if path.suffix == '':
        try:
            # Read only the first 64 bytes to check shebang
            with open(path, 'rb') as f:
                head = f.read(64)
                # Look for standard shebangs like #!/usr/bin/env python or #!/usr/bin/python
                if b'python' in head and b'#!' in head:
                    return True
        except Exception:
            return False
    return False


def run_command(cmd):
    """Runs a subprocess command and returns (returncode, stdout, stderr)."""
    try:
        # We set force-exclude so ruff doesn't format files unrelated to the project context
        # if they happen to be in the list (though we are scanning current dir).
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, '', str(e)


def process_file(file_path_str) -> None:
    """Worker function to process a single file.
    1. Run ruff check (fixes)
    2. Run ruff format (styling).
    """
    path = Path(file_path_str)

    # --- Step 1: Apply Fixes (Linter) ---
    # --fix: apply fixes
    # --unsafe-fixes: apply fixes even if they might change semantics
    # --line-length 79: ensure line length rules are respected during fixes
    # --select ALL: strict checking (optional, but 'apply all' usually implies broad scope.
    #               However, defaults are usually safer. We stick to defaults + unsafe here
    #               to avoid overwhelming noise, as 'ALL' is extremely strict).
    check_cmd = [
        'ruff',
        'check',
        '--fix',
        '--unsafe-fixes',
        '--line-length',
        '79',
        '--quiet',  # We handle output manually
        str(path),
    ]

    rc_check, out_check, err_check = run_command(check_cmd)

    # --- Step 2: Apply Formatting (Styler) ---
    # --quote-style single: force single quotes
    # --line-length 79: force wrap at 79
    format_cmd = [
        'ruff',
        'format',
        '--config',
        '/data/data/com.termux/files/home/.config/ruff/ruff.toml',
        str(path),
    ]

    rc_fmt, out_fmt, err_fmt = run_command(format_cmd)

    # --- Error Handling ---
    # We only print if there were issues.
    # Ruff quiet mode generally suppresses successful file messages.

    output = []

    # If check failed or had stderr output (warnings)
    if rc_check != 0 or err_check.strip():
        output.append(f'--- Issues fixing {path.name} ---')
        if err_check.strip():
            output.append(err_check.strip())
        if out_check.strip():
            output.append(out_check.strip())

    # If format failed (rare, usually syntax error)
    if rc_fmt != 0 or err_fmt.strip():
        output.append(f'--- Issues formatting {path.name} ---')
        if err_fmt.strip():
            output.append(err_fmt.strip())

    if output:
        with print_lock:
            print('\n'.join(output))
            sys.stdout.flush()


def get_all_files(root_dir):
    """Recursively finds all python files."""
    py_files = []
    for root, dirs, files in os.walk(root_dir):
        # Skip common ignore dirs to save time
        dirs[:] = [
            d
            for d in dirs
            if d
            not in {
                '.git',
                '.venv',
                'venv',
                '__pycache__',
                'build',
                'dist',
                'node_modules',
            }
        ]

        for file in files:
            file_path = Path(root) / file
            if is_python_file(file_path):
                py_files.append(str(file_path))
    return py_files


def main() -> None:
    # Check if ruff is installed
    try:
        subprocess.run(['ruff', '--version'], capture_output=True, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("Error: 'ruff' is not installed or not in PATH.")
        print('Please run: pip install ruff')
        sys.exit(1)

    root_dir = os.getcwd()
    files = get_all_files(root_dir)

    if not files:
        return  # No python files found, exit silently

    # Use Multiprocessing to speed up
    # We use fewer processes than max CPU if file count is low to avoid overhead
    num_procs = min(len(files), cpu_count())

    with Pool(num_procs) as pool:
        pool.map(process_file, files)


if __name__ == '__main__':
    main()
