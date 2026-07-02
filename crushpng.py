#!/data/data/com.termux/files/usr/bin/python
"""
A parallel PNG optimizer using pngcrush.
Recursively finds PNG files in the current directory and optimizes them in place.
"""

import os
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm


def find_png_files(directory: str) -> list:
    """
    Recursively finds all .png files in the given directory.

    Args:
        directory: The root directory to search.

    Returns:
        A list of paths to PNG files.
    """
    png_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(".png"):
                png_files.append(os.path.join(root, file))
    return png_files


def optimize_png(file_path: str) -> tuple:
    """
    Optimizes a single PNG file using pngcrush.

    Args:
        file_path: Path to the PNG file.

    Returns:
        A tuple of (success_boolean, file_path, error_message or None).
    """
    try:
        # -ow: Overwrite original file
        # -reduce: Perform lossless reductions
        subprocess.run(["pngcrush", "-ow", "-reduce", file_path], 
                       check=True, capture_output=True)
        return True, file_path, None
    except subprocess.CalledProcessError as e:
        return False, file_path, e.stderr.decode().strip()
    except FileNotFoundError:
        return False, file_path, "pngcrush not found"


def main() -> None:
    """
    Main function to orchestrate parallel PNG optimization.
    """
    current_dir = os.getcwd()
    png_files = find_png_files(current_dir)

    if not png_files:
        print("No PNG files found in the current directory.")
        return

    print(f"Found {len(png_files)} PNG files to optimize.")

    # Using cpu_count for better scaling across different devices
    max_workers = os.cpu_count() or 4
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(optimize_png, file): file for file in png_files}
        results = []

        with tqdm(total=len(png_files), desc="Optimizing PNGs", unit="file") as pbar:
            for future in as_completed(futures):
                results.append(future.result())
                pbar.update(1)

    # Print summary
    success_count = sum(1 for r in results if r[0])
    failures = [r for r in results if not r[0]]
    
    print(f"\nOptimization complete. Success: {success_count}/{len(png_files)} files.")
    
    if failures:
        print("\nFailures:")
        for _, path, error in failures[:10]: # Limit output
            print(f"- {os.path.relpath(path)}: {error}")
        if len(failures) > 10:
            print(f"... and {len(failures) - 10} more.")


if __name__ == "__main__":
    main()
