#!/usr/bin/env python3
"""
Finds files modified, created, changed, or accessed within a specified number of minutes.
Default is 60 minutes.
"""

import os
import sys
import time


def parse_minutes() -> float:
    """
    Parses the number of minutes from command line arguments.
    Returns 60.0 if no argument is provided.
    """
    if len(sys.argv) == 1:
        return 60.0

    try:
        return float(sys.argv[1])
    except ValueError:
        print(f"Usage: {sys.argv[0]} [minutes]")
        sys.exit(1)


def main() -> None:
    """
    Walks through the current directory and prints paths of files
    accessed, modified, or changed since the calculated cutoff time.
    """
    minutes = parse_minutes()
    cutoff = time.time() - (minutes * 60)

    for root, _, files in os.walk("."):
        for file in files:
            path = os.path.join(root, file)

            try:
                stats = os.stat(path)
                # Check creation/metadata change, modification, and access times
                if any(t >= cutoff for t in (stats.st_mtime, stats.st_ctime, stats.st_atime)):
                    print(path)
            except OSError:
                continue


if __name__ == "__main__":
    main()
