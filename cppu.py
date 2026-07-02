#!/data/data/com.termux/files/usr/bin/env python3
"""
A threaded C++ formatter using clang-format and ThreadPoolExecutor.
Ideal for environments where process overhead is high or I/O bound tasks dominate.
"""

from time import perf_counter
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor

# List of file extensions to search for
FILE_EXTENSIONS = {".c", ".cpp", ".cxx", ".cc", ".h", ".hh", ".hpp", ".hxx"}


def format_file(file_path: str) -> bool:
    """
    Runs clang-format on a single file.

    Args:
        file_path: Path to the file.

    Returns:
        True if successful, False otherwise.
    """
    print(f"Formatting {os.path.relpath(file_path)}")
    try:
        # Running an external command like clang-format releases the GIL,
        # allowing threads to run concurrently while waiting for the command.
        subprocess.run(["clang-format", "-i", file_path], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        if isinstance(e, FileNotFoundError):
            print("Error: clang-format not found.")
        return False


def find_files(dir_path: str = ".") -> list:
    """
    Recursively finds all C/C++ source and header files.

    Args:
        dir_path: Root directory to search.

    Returns:
        List of file paths.
    """
    all_files = []
    for root, _, files in os.walk(dir_path):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in FILE_EXTENSIONS:
                all_files.append(os.path.join(root, file))
    return all_files


def main() -> None:
    """
    Main function to execute threaded formatting.
    """
    start = perf_counter()
    files_to_format = find_files()
    if not files_to_format:
        print("No files found.")
        return

    print(f"Formatting {len(files_to_format)} files using ThreadPoolExecutor...")

    # ThreadPoolExecutor is lightweight and doesn't require pickling arguments
    with ThreadPoolExecutor() as executor:
        results = list(executor.map(format_file, files_to_format))
        count = sum(1 for success in results if success)

    duration = perf_counter() - start
    print(f"Successfully formatted {count}/{len(files_to_format)} files in {duration:.2f} seconds.")


if __name__ == "__main__":
    main()
