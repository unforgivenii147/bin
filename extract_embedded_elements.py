#!/data/data/com.termux/files/usr/bin/env python3
"""
A utility to scan HTML files and extract embedded base64 assets (images, fonts, PDFs, etc.).
Assets are saved in a directory named 'extracted_base64' with unique SHA256 hashes as filenames.
"""

from __future__ import annotations

import base64
import hashlib
from pathlib import Path
from typing import TYPE_CHECKING

import regex as re

if TYPE_CHECKING:
    from collections.abc import Iterable

OUTPUT_DIR = Path("extracted_base64")
HTML_EXTENSIONS = {".html", ".htm"}
DATA_URL_RE = re.compile(
    r"data:(?P<mime>[-\w.+/]+);base64,(?P<data>[A-Za-z0-9+/=\s]+)",
    re.IGNORECASE,
)
MIME_EXTENSION_MAP: dict[str, str] = {
    "image/png": "png",
    "image/jpeg": "jpg",
    "image/jpg": "jpg",
    "image/gif": "gif",
    "image/webp": "webp",
    "image/svg+xml": "svg",
    "application/pdf": "pdf",
    "application/octet-stream": "bin",
    "font/woff": "woff",
    "font/woff2": "woff2",
    "application/font-woff": "woff",
    "application/font-woff2": "woff2",
}


def iter_html_files(root: Path) -> Iterable[Path]:
    """
    Recursively yields Path objects for HTML files under the root directory.
    
    Args:
        root (Path): The starting directory for searching.
        
    Yields:
        Path: The next HTML file found.
    """
    for path in root.rglob("*"):
        if path.suffix.lower() in HTML_EXTENSIONS and path.is_file():
            yield path


def infer_extension(mime: str) -> str:
    """
    Infers a file extension from a MIME type.
    
    Args:
        mime (str): The MIME type string (e.g., 'image/png').
        
    Returns:
        str: The inferred extension (e.g., 'png').
    """
    return MIME_EXTENSION_MAP.get(mime.lower(), mime.rsplit("/", maxsplit=1)[-1])


def decode_base64(data: str) -> bytes:
    """
    Cleans and decodes a base64 encoded string.
    
    Args:
        data (str): The raw base64 data string.
        
    Returns:
        bytes: The decoded binary data.
    """
    cleaned = "".join(data.split())
    return base64.b64decode(cleaned, validate=False)


def content_hash(data: bytes) -> str:
    """
    Generates a SHA256 hash of the given binary data.
    
    Args:
        data (bytes): The binary data to hash.
        
    Returns:
        str: The hexadecimal SHA256 digest.
    """
    return hashlib.sha256(data).hexdigest()


def extract_from_html(html: str) -> Iterable[tuple[str, bytes]]:
    """
    Scans HTML source for embedded data URLs and decodes them.
    
    Args:
        html (str): The HTML source content.
        
    Yields:
        tuple[str, bytes]: A tuple of (MIME type, decoded binary data).
    """
    for match in DATA_URL_RE.finditer(html):
        mime = match.group("mime")
        raw_data = match.group("data")
        try:
            decoded = decode_base64(raw_data)
        except Exception:
            continue
        yield mime, decoded


def save_asset(mime: str, data: bytes) -> Path:
    """
    Saves binary data to a file in the output directory if it doesn't already exist.
    Filename is based on the SHA256 hash of the content.
    
    Args:
        mime (str): The MIME type of the asset.
        data (bytes): The binary data to save.
        
    Returns:
        Path: The path to the saved asset file.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ext = infer_extension(mime)
    digest = content_hash(data)
    filename = f"{digest}.{ext}"
    path = OUTPUT_DIR / filename
    if not path.exists():
        path.write_bytes(data)
    return path


def main() -> None:
    """
    Main entry point: scans the current directory for HTML files and extracts
    unique embedded base64 assets.
    """
    root = Path.cwd()
    seen_hashes = set()
    extracted_count = 0
    
    for html_file in iter_html_files(root):
        print(f"Scanning: {html_file.relative_to(root)}")
        try:
            html = html_file.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            print(f"Error reading {html_file}: {e}")
            continue
            
        for mime, data in extract_from_html(html):
            digest = content_hash(data)
            if digest in seen_hashes:
                continue
            seen_hashes.add(digest)
            save_asset(mime, data)
            extracted_count += 1

    print(f"\nDone! Extracted {extracted_count} unique assets to '{OUTPUT_DIR}'")


if __name__ == "__main__":
    main()
