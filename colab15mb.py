#!/data/data/com.termux/files/usr/bin/python
"""
Compress small site-packages from Google Colab.

This module provides a utility to identify and compress small packages
from the Google Colab environment's site-packages directory, making it
easier to export and reuse lightweight dependencies.
"""

import os
import site
import tarfile
from typing import List
from pathlib import Path

try:
    from google.colab import files
except ImportError:
    # Fallback for local testing
    files = None


def get_folder_size(path: Path) -> int:
    """
    Calculate the total size of a folder in bytes.

    Args:
        path: The Path object pointing to the directory.

    Returns:
        The total size of the folder in bytes.
    """
    total = 0
    for root, _, files_list in os.walk(path):
        for f in files_list:
            fp = Path(root) / f
            try:
                if fp.is_file():
                    total += fp.stat().st_size
            except OSError:
                continue
    return total


def compress_small_site_packages(max_size_mb: float = 15.0) -> None:
    """
    Compress packages in site-packages that are smaller than the specified size.

    Args:
        max_size_mb: The maximum size of a package (in MB) to be included in the archive.
    """
    try:
        site_packages_dir = Path(site.getsitepackages()[0])
    except (IndexError, AttributeError):
        print("Error: Could not determine site-packages directory.")
        return

    output_file = "site-packages-small.tar.gz"

    print(f"Searching in: {site_packages_dir}")
    print(f"Max size: {max_size_mb} MB")

    with tarfile.open(output_file, "w:gz") as tar:
        for item in site_packages_dir.iterdir():
            if item.is_dir():
                # Include folder if total size <= max_size_mb
                folder_size_mb = get_folder_size(item) / (1024 * 1024)
                if folder_size_mb <= max_size_mb:
                    print(f"Including folder {item.name} ({folder_size_mb:.2f} MB)")
                    for root, _, files_list in os.walk(item):
                        for f in files_list:
                            if not f.endswith(".pyc"):
                                full_path = Path(root) / f
                                arcname = full_path.relative_to(site_packages_dir)
                                tar.add(full_path, arcname=arcname)

            elif item.is_file():
                # Include individual file if size <= max_size_mb
                file_size_mb = item.stat().st_size / (1024 * 1024)
                if file_size_mb <= max_size_mb and not item.name.endswith(".pyc"):
                    print(f"Including file {item.name} ({file_size_mb:.2f} MB)")
                    arcname = item.relative_to(site_packages_dir)
                    tar.add(item, arcname=arcname)

    print(f"Archive created: {output_file}")
    if files:
        files.download(output_file)
    else:
        print("google.colab not found, skipping download.")


if __name__ == "__main__":
    compress_small_site_packages(max_size_mb=15)
