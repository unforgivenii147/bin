#!/data/data/com.termux/files/usr/bin/python
"""
Export site-packages from Google Colab to Google Drive.

This script identifies installed packages in a Colab environment and
exports them to Google Drive, excluding system packages like pip and setuptools.
Directories are zipped for efficient storage.
"""

import os
import shutil
import site
import zipfile
from pathlib import Path
from typing import Tuple

try:
    from google.colab import drive
except ImportError:
    drive = None


def excluded(name: str) -> bool:
    """
    Check if a package should be excluded from the export.

    Args:
        name: The name of the package.

    Returns:
        True if the package should be excluded, False otherwise.
    """
    exclude_prefixes = ("setuptools", "pip")
    return name.startswith(exclude_prefixes)


def export_site_packages() -> None:
    """
    Main function to export site-packages to Google Drive.
    """
    if drive:
        drive.mount("/content/drive")
    else:
        print("Warning: google.colab.drive not found. Skipping mount.")

    # Resolve system site-packages
    try:
        site_pkgs = Path(site.getsitepackages()[0])
    except (IndexError, AttributeError):
        print("Error: Could not determine site-packages directory.")
        return

    # Output directory
    out_dir = Path("/content/drive/MyDrive/wheels")
    out_dir.mkdir(parents=True, exist_ok=True)

    copied_files = 0
    zipped_dirs = 0

    print(f"Exporting from: {site_pkgs}")
    print(f"Saving to: {out_dir}")

    # Iterate top-level entries
    for entry in site_pkgs.iterdir():
        name = entry.name

        if excluded(name):
            continue

        # ---- Copy top-level files ----
        if entry.is_file():
            try:
                shutil.copy2(entry, out_dir / name)
                copied_files += 1
            except Exception as e:
                print(f"Failed to copy file {name}: {e}")

        # ---- Zip top-level directories ----
        elif entry.is_dir():
            zip_path = out_dir / f"{name}.zip"
            try:
                with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
                    for root, _, files_list in os.walk(entry):
                        for f in files_list:
                            if not f.endswith(".pyc"):
                                fp = Path(root) / f
                                try:
                                    zf.write(fp, fp.relative_to(site_pkgs))
                                except Exception as e:
                                    print(f"Error writing {fp} to zip: {e}")
                zipped_dirs += 1
            except Exception as e:
                print(f"Failed to zip directory {name}: {e}")

    # Report
    print("\nExport completed.")
    print(f"Site-packages source : {site_pkgs}")
    print(f"Output directory     : {out_dir}")
    print(f"Top-level files copied : {copied_files}")
    print(f"Top-level dirs zipped  : {zipped_dirs}")
    print("Excluded packages     : setuptools, pip")


if __name__ == "__main__":
    export_site_packages()
