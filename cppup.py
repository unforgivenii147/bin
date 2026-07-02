#!/data/data/com.termux/files/usr/bin/env python3
"""
A parallel C++ formatter using clang-format and ProcessPoolExecutor.
Searches for C/C++ source and header files recursively and formats them in place.
"""

from time import perf_counter
import os
import subprocess
from concurrent.futures import ProcessPoolExecutor

# List of file extensions to search for
FILE_EXTENSIONS = {".c", ".cpp", ".cxx", ".cc", ".h", ".hh", ".hpp", ".hxx"}


def format_file(file_path: str) -> bool:
    """
    Runs clang-format on a single file.

    Args:
        file_path: Absolute or relative path to the file.

    Returns:
        True if formatting was successful, False otherwise.
    """
    print(f"Formatting {os.path.relpath(file_path)}")
    try:
        # -i flag modifies the file in place
        subprocess.run(["clang-format", "-i", file_path], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        if isinstance(e, FileNotFoundError):
            print("Error: clang-format not found. Please install it.")
        else:
            print(f"Error formatting {file_path}: {e}")
        return False


def find_files(dir_path: str = ".") -> list:
    """
    Finds all files with specified C++ extensions recursively.

    Args:
        dir_path: The root directory to start the search.

    Returns:
        A list of file paths.
    """
    all_files = []
    try:
        for root, _, files in os.walk(dir_path):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in FILE_EXTENSIONS:
                    all_files.append(os.path.join(root, file))
    except Exception as e:
        print(f"Error traversing directory: {e}")
    return all_files


def main() -> None:
    """
    Main entry point for the parallel formatter.
    """
    start = perf_counter()
    files_to_format = find_files()

    if not files_to_format:
        print("No files found with the specified extensions.")
        return

    print(f"Formatting {len(files_to_format)} files using ProcessPoolExecutor...")

    # Max_workers defaults to the number of processors on the machine
    # Using a fixed 8 or defaulting to None (which is better for general use)
    with ProcessPoolExecutor() as executor:
        results = list(executor.map(format_file, files_to_format))
        count = sum(1 for success in results if success)

    duration = perf_counter() - start
    print(f"Successfully formatted {count}/{len(files_to_format)} files in {duration:.2f} seconds.")


if __name__ == "__main__":
    main()
