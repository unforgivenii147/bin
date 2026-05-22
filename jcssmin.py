#!/data/data/com.termux/files/usr/bin/env python3
"""Recursively minify all JS and CSS files in the current directory.
OVERWRITES the original file.
Uses multiprocessing for speed.
"""

import multiprocessing
import os

from rcssmin import cssmin
from rjsmin import jsmin


def process_file(path: str) -> str:
    """Why: Single worker task, safe to call in multiprocessing."""
    try:
        with open(path, encoding="utf-8") as f:
            content = f.read()

        if path.endswith(".js"):
            minified = jsmin(content)
        elif path.endswith(".css"):
            minified = cssmin(content)
        else:
            return f"SKIP (unknown type) → {path}"

        with open(path, "w", encoding="utf-8") as f:
            f.write(minified)

        return f"OK → {path}"

    except Exception as e:
        return f"ERR ({path}): {e}"


def collect_files() -> list:
    """Why: Avoid double-minification of .min.js & .min.css."""
    targets = []
    root = os.getcwd()

    for base, _, files in os.walk(root):
        for name in files:
            path = os.path.join(base, name)

            if name.endswith(".js") and not name.endswith(".min.js"):
                targets.append(path)

            elif name.endswith(".css") and not name.endswith(".min.css"):
                targets.append(path)

    return targets


def main() -> None:
    files = collect_files()

    if not files:
        print("No JS or CSS files found.")
        return

    print(f"Found {len(files)} files. Starting multiprocessing...")

    with multiprocessing.Pool(multiprocessing.cpu_count()) as pool:
        for result in pool.imap_unordered(process_file, files):
            print(result)


if __name__ == "__main__":
    main()
