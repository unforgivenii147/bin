#!/usr/bin/env python3
import os
import tarfile
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed

import regex as re

# Regex pattern to match URLs
url_pattern = re.compile(r'https?://[^\s"\']+')

# Read allowed extensions from file
with open('/sdcard/ext', 'r', encoding='utf-8') as f:
    allowed_exts = set(line.strip().lower() for line in f if line.strip())


# Helper function to extract URLs from text content
def extract_urls_from_text(content):
    return set(url_pattern.findall(content))


# Extract URLs from a regular file
def extract_urls_from_file(filepath):
    urls = set()
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            urls.update(extract_urls_from_text(content))
    except Exception as e:
        print(f'Failed to read {filepath}: {e}')
    return urls


# Extract URLs from tar archives
def extract_urls_from_tar(filepath):
    urls = set()
    try:
        mode = 'r:*'  # detect compression automatically
        with tarfile.open(filepath, mode) as tar:
            for member in tar.getmembers():
                if member.isfile():
                    f = tar.extractfile(member)
                    if f:
                        try:
                            content = f.read().decode('utf-8', errors='ignore')
                            urls.update(extract_urls_from_text(content))
                        except:
                            pass
    except Exception as e:
        print(f'Failed to read tar {filepath}: {e}')
    return urls


# Extract URLs from zip/whl files
def extract_urls_from_zip(filepath):
    urls = set()
    try:
        with zipfile.ZipFile(filepath, 'r') as zf:
            for name in zf.namelist():
                try:
                    with zf.open(name) as f:
                        content = f.read().decode('utf-8', errors='ignore')
                        urls.update(extract_urls_from_text(content))
                except:
                    pass
    except Exception as e:
        print(f'Failed to read zip {filepath}: {e}')
    return urls


"""
# Extract URLs from 7z files
def extract_urls_from_7z(filepath):
    urls = set()
    try:
        with py7zr.SevenZipFile(filepath, mode='r') as archive:
            all_files = archive.readall()
            for name, bio in all_files.items():
                try:
                    content = bio.read().decode('utf-8', errors='ignore')
                    urls.update(extract_urls_from_text(content))
                except:
                    pass
    except Exception as e:
        print(f"Failed to read 7z {filepath}: {e}")
    return urls
"""


# Determine extraction method based on extension
def extract_urls(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    if ext in allowed_exts:
        return extract_urls_from_file(filepath)
    elif ext in ['.zip', '.whl']:
        return extract_urls_from_zip(filepath)
    elif ext.startswith('.tar') or ext in [
            '.tar.gz', '.tar.xz', '.tar.zst', '.tar.7z'
    ]:
        return extract_urls_from_tar(filepath)
    #    elif ext == '.7z':
    #        return extract_urls_from_7z(filepath)
    return set()


# Gather all files recursively, skipping hidden dirs
file_paths = []
for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if not d.startswith('.')]
    for file in files:
        file_paths.append(os.path.join(root, file))

# Extract URLs concurrently
all_urls = set()
with ThreadPoolExecutor() as executor:
    futures = [executor.submit(extract_urls, fp) for fp in file_paths]
    for future in as_completed(futures):
        all_urls.update(future.result())

# Save unique URLs to urls.txt
with open('urls.txt', 'w', encoding='utf-8') as f:
    for url in sorted(all_urls):
        f.write(url + '\n')

print(f'Extracted {len(all_urls)} unique URLs to urls.txt')
