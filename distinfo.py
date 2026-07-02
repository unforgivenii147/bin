#!/data/data/com.termux/files/usr/bin/env python3
"""
Analyzes Python site-packages to find packages that have multiple versions installed.
This is useful for identifying redundant or conflicting package installations.
"""

import os
import site
import re
from collections import defaultdict


def get_site_packages_dirs():
    """
    Returns a list of system and user site-packages directories.

    Returns:
        list: Deduped list of site-packages directory paths.
    """
    dirs = []
    try:
        dirs.extend(site.getsitepackages())
    except Exception:
        pass

    # Include user site-packages
    dirs.append(site.getusersitepackages())

    # Deduplicate while preserving order
    return list(dict.fromkeys(dirs))


def parse_pkg_info(dirname):
    """
    Parses the package name and version from .dist-info or .egg-info directory names.

    Args:
        dirname (str): The name of the directory (e.g., "numpy-2.2.5.dist-info").

    Returns:
        tuple: (package_name, version) or (None, None) if not a match.
    """
    # Regex handles standard dist-info and egg-info naming conventions
    m = re.match(r"^(.+?)-([0-9].*?)(\.dist-info|\.egg-info)$", dirname)
    if m:
        return m.group(1).lower(), m.group(2)
    return None, None


def find_multiple_versions() -> None:
    """
    Scans site-packages directories and reports packages with multiple versions.
    """
    pkg_versions = defaultdict(set)

    for sp_dir in get_site_packages_dirs():
        if not os.path.isdir(sp_dir):
            continue

        for entry in os.listdir(sp_dir):
            if entry.endswith((".dist-info", ".egg-info")):
                name, version = parse_pkg_info(entry)
                if name:
                    pkg_versions[name].add(version)

    # Report packages that have more than one version installed
    found_duplicates = False
    for pkg, versions in sorted(pkg_versions.items()):
        if len(versions) > 1:
            found_duplicates = True
            print(f"\nPackage: {pkg}")
            for v in sorted(versions):
                print(f"  - Version: {v}")
    
    if not found_duplicates:
        print("No duplicate package versions found.")
    
    print("\nDone.")


if __name__ == "__main__":
    find_multiple_versions()
