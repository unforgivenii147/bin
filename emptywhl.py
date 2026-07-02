#!/data/data/com.termux/files/usr/bin/env python3
"""
Scans the current directory for Python .whl (wheel) files and identifies those that are "empty".
A wheel is considered empty if all its recorded files are within its .dist-info directory.
"""

import csv
import os
import zipfile


def is_empty_wheel(wheel_path: str) -> bool:
    """
    Checks if a wheel file is "empty".

    Args:
        wheel_path (str): Path to the .whl file.

    Returns:
        bool: True if empty, False otherwise.
    """
    try:
        with zipfile.ZipFile(wheel_path, "r") as z:
            # Find the dist-info directory inside the wheel
            dist_info_dirs = [name for name in z.namelist() if name.endswith(".dist-info/") or (".dist-info" in name and "/" not in name.split(".dist-info")[1])]
            if not dist_info_dirs:
                return False
            
            # Standard wheels have one .dist-info dir
            dist_info = dist_info_dirs[0].rstrip("/")
            record_path = dist_info + "/RECORD"
            
            if record_path not in z.namelist():
                return False

            with z.open(record_path) as f:
                # Decode bytes to string for csv reader
                content = (line.decode("utf-8") for line in f)
                reader = csv.reader(content)
                for row in reader:
                    if not row:
                        continue
                    file_path = row[0]
                    # If any file is outside the .dist-info directory, it's not empty
                    if not file_path.startswith(dist_info + "/"):
                        return False
    except (zipfile.BadZipFile, OSError, KeyError):
        return False
        
    return True


def main() -> None:
    """
    Main entry point for the emptywhl script.
    """
    wheels = [f for f in os.listdir(".") if f.endswith(".whl")]
    if not wheels:
        print("No .whl files found in the current directory.")
        return
    
    print(f"Checking {len(wheels)} wheel(s)...")
    empty = [wheel for wheel in wheels if is_empty_wheel(wheel)]
    
    if not empty:
        print("No empty wheels found.")
        return
    
    print(f"Found {len(empty)} empty wheel(s):")
    for w in sorted(empty):
        print(f"  - {w}")


if __name__ == "__main__":
    main()
