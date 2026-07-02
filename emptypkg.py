#!/data/data/com.termux/files/usr/bin/env python3
"""
Identifies "empty" Python packages in site-packages.
A package is considered empty if all files listed in its RECORD file 
are located within its own .dist-info directory.
"""

import csv
import os
import pathlib
import sysconfig


def is_empty_package(dist_info_path: str) -> bool:
    """
    Returns True if all files listed in the package's RECORD are inside its .dist-info dir.

    Args:
        dist_info_path (str): Path to the .dist-info directory.

    Returns:
        bool: True if the package is likely "empty", False otherwise.
    """
    record_file = os.path.join(dist_info_path, "RECORD")
    if not pathlib.Path(record_file).is_file():
        return False

    dist_info_dir = pathlib.Path(dist_info_path).resolve()
    parent_dir = dist_info_dir.parent

    try:
        with open(record_file, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                if not row:
                    continue
                rel_path = row[0]
                # RECORD lists relative paths from the site-packages root
                abs_path = (parent_dir / rel_path).resolve()
                
                # If the file is NOT inside the .dist-info directory, it's not an empty package
                if dist_info_dir not in abs_path.parents and abs_path != dist_info_dir:
                    return False
    except (OSError, csv.Error):
        return False
        
    return True


def find_empty_packages(site_packages: str):
    """
    Scans site-packages for .dist-info directories and checks for empty packages.

    Args:
        site_packages (str): Path to the site-packages directory.

    Returns:
        list: List of paths to .dist-info directories of empty packages.
    """
    empty = []
    if not os.path.isdir(site_packages):
        return empty
        
    for entry in os.listdir(site_packages):
        if entry.endswith(".dist-info"):
            dist_info_path = os.path.join(site_packages, entry)
            if is_empty_package(dist_info_path):
                empty.append(dist_info_path)
    return empty


def main() -> None:
    """
    Main entry point for the emptypkg script.
    """
    # Use purelib as it's the standard site-packages for non-platform-specific code
    site_packages = sysconfig.get_paths()["purelib"]
    print(f"Scanning for empty packages in: {site_packages}")
    
    empty = find_empty_packages(site_packages)
    if not empty:
        print("No empty packages found.")
        return
    
    print(f"Found {len(empty)} empty package(s):")
    for p in sorted(empty):
        print(f"  - {os.path.basename(p)}")


if __name__ == "__main__":
    main()
