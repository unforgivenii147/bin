#!/data/data/com.termux/files/usr/bin/python
"""
A utility to fetch the download size of a URL or a list of URLs from a file.
Optionally downloads files smaller than a specified limit (default 1MB).
"""

import argparse
import sys
import urllib.request
import urllib.error
import urllib.parse
from pathlib import Path
import os
from typing import Optional

MAX_DOWNLOAD_SIZE = 1 * 1024 * 1024  # 1 MB


def fetch_content_length(url: str) -> Optional[int]:
    """
    Attempts to fetch the Content-Length of a URL using a HEAD request or a partial GET.

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
        # 405 Method Not Allowed or 403 Forbidden -> try partial GET
        if e.code not in (405, 403):
            raise
    except Exception:
        pass

    try:
        # Fallback: GET headers only (partial download)
        request = urllib.request.Request(url, method="GET")
        request.add_header("Range", "bytes=0-0")
        with urllib.request.urlopen(request, timeout=10) as response:
            length = response.headers.get("Content-Length")
            return int(length) if length else None
    except Exception:
        return None


def format_size(size_bytes: int) -> str:
    """
    Formats a size in bytes into a human-readable string (KB, MB, GB, etc.).

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


def download_file(url: str, dest_dir: Path) -> None:
    """
    Downloads a file from a URL to the specified directory.

    Args:
        url (str): The URL to download.
        dest_dir (Path): The destination directory.
    """
    filename = Path(urllib.parse.urlparse(url).path).name or "downloaded_file"
    dest_file = dest_dir / filename
    try:
        urllib.request.urlretrieve(url, dest_file)
        print(f"Downloaded: {dest_file}")
    except Exception as e:
        print(f"Failed to download {url}: {e}")


def process_url(url: str, download_dir: Optional[Path] = None) -> str:
    """
    Fetches the size of a URL and optionally downloads it if under the size limit.

    Args:
        url (str): The URL to process.
        download_dir (Optional[Path]): The directory to download to.

    Returns:
        str: A string containing the URL and its size or error status.
    """
    try:
        size = fetch_content_length(url)
        if size is None:
            return f"{url}\tUnknown"

        size_str = format_size(size)
        print(f"URL: {url}, Size: {size_str}")

        # Optional download if under limit
        if download_dir and size <= MAX_DOWNLOAD_SIZE:
            # Note: In a headless environment, this input might block.
            # Assuming Termux user interaction.
            user_input = input(f"Do you want to download this file (size: {size_str})? (y/n): ").strip().lower()
            if user_input == "y":
                download_file(url, download_dir)
            else:
                print("Download skipped.")
        elif download_dir:
            print(f"File ({size_str}) exceeds limit of {format_size(MAX_DOWNLOAD_SIZE)}.")

        return f"{url}\t{size_str}"
    except Exception as exc:
        return f"{url}\tError: {exc}"


def main() -> None:
    """
    Main entry point for the dsized script.
    """
    parser = argparse.ArgumentParser(description="Show download size of a URL or URLs from a file")
    parser.add_argument("input", help="Download URL or file containing URLs")
    parser.add_argument("-d", "--download", help="Directory to download files smaller than 1MB")
    args = parser.parse_args()

    # Set default download directory to user's Downloads folder if not specified
    if args.download:
        download_dir = Path(args.download)
    else:
        download_dir = Path(os.path.expanduser("~/Downloads"))

    input_path = Path(args.input)
    if input_path.is_file():
        download_dir.mkdir(parents=True, exist_ok=True)
        lines = input_path.read_text(encoding="utf-8").splitlines()
        updated_lines = [process_url(line.strip(), download_dir) for line in lines if line.strip()]
        # Note: This overwrites the original file with size info.
        input_path.write_text("\n".join(updated_lines), encoding="utf-8")
        print(f"Updated file: {input_path} ({len(updated_lines)} URLs processed)")
    else:
        # Only create download dir if we are actually downloading a single URL
        # But process_url checks size limit, so we can defer.
        print(process_url(args.input, download_dir if args.download else None))


if __name__ == "__main__":
    main()
