#!/data/data/com.termux/files/usr/bin/python
"""
A simple utility to fetch and report the download size of one or more URLs.
Unlike dsized.py, this script focuses solely on reporting sizes.
"""

import argparse
import sys
import urllib.request
import urllib.error
from pathlib import Path
from typing import Optional


def fetch_content_length(url: str) -> Optional[int]:
    """
    Attempts to fetch the Content-Length of a URL.

    Args:
        url (str): The URL to check.

    Returns:
        Optional[int]: The content length in bytes, or None if it could not be determined.
    """
    try:
        request = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(request, timeout=10) as response:
            length = response.headers.get("Content-Length")
            if length:
                return int(length)
    except urllib.error.HTTPError as e:
        if e.code not in (405, 403):
            raise
    except Exception:
        pass

    try:
        request = urllib.request.Request(url, method="GET")
        request.add_header("Range", "bytes=0-0")
        with urllib.request.urlopen(request, timeout=10) as response:
            length = response.headers.get("Content-Length")
            return int(length) if length else None
    except Exception:
        return None


def format_size(size_bytes: int) -> str:
    """
    Formats a size in bytes into a human-readable string.

    Args:
        size_bytes (int): The size in bytes.

    Returns:
        str: Human-readable size string.
    """
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(size_bytes)
    for unit in units:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} PB"


def process_url(url: str) -> str:
    """
    Fetches the size of a URL and returns a formatted report string.

    Args:
        url (str): The URL to process.

    Returns:
        str: A string containing the URL and its size.
    """
    try:
        size = fetch_content_length(url)
        if size is None:
            print(f"{url[:50]}... : Unknown size")
            return f"{url}\tUnknown"
        
        size_mb = size / (1024 * 1024)
        print(f"{url[:50]}... : {size_mb:.2f} MB")
        return f"{url}\t{format_size(size)}"
    except Exception as exc:
        return f"{url}\tError: {exc}"


def main() -> None:
    """
    Main entry point for the dsize script.
    """
    parser = argparse.ArgumentParser(description="Show download size of a URL or URLs from a file")
    parser.add_argument("input", help="Download URL or file containing URLs")
    args = parser.parse_args()

    input_path = Path(args.input)
    if input_path.is_file():
        # File mode: update each line with size
        lines = input_path.read_text(encoding="utf-8").splitlines()
        updated_lines = [process_url(line.strip()) for line in lines if line.strip()]

        # Overwrite file with updated info
        input_path.write_text("\n".join(updated_lines), encoding="utf-8")
        print(f"Updated file: {input_path} ({len(updated_lines)} URLs processed)")
    else:
        # Single URL mode
        result = process_url(args.input)
        if "\t" in result:
            print(f"Result: {result.split('\t')[1]}")


if __name__ == "__main__":
    main()
