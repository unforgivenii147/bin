#!/usr/bin/env python3
"""
path: ./extract_urls.py
"""

from __future__ import annotations

import os
import tarfile
import threading
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Iterable, Set
from urllib.parse import urlparse, urlunparse

import regex as re

try:
    import zstandard as zstd
except Exception:
    zstd = None

URL_RE = re.compile(
    r"""(https?://[^\s<>"\']+|\bwww\.[^\s<>"\']+\b|\b[^\s<>"\']+\.(com|net|org)[^\s<>"\']*)"""
)

GITHUB_RE = re.compile(r'(?i)github\.com')

MAX_WORKERS = os.cpu_count() or 4

all_urls: Set[str] = set()
git_urls: Set[str] = set()
git_urls_classified: Dict[str, Set[str]] = {
    'repo': set(),
    'issue': set(),
    'pull': set(),
    'release': set(),
    'raw': set(),
    'clone': set(),
    'other': set(),
}

lock = threading.Lock()


def normalize_url(url: str) -> str:
    try:
        p = urlparse(url)
        scheme = p.scheme.lower()
        netloc = p.netloc.lower()

        if (scheme == 'http' and netloc.endswith(':80')) or (
            scheme == 'https' and netloc.endswith(':443')
        ):
            netloc = netloc.rsplit(':', 1)[0]

        path = p.path.rstrip('/') or '/'

        return urlunparse((scheme, netloc, path, '', p.query, ''))
    except Exception:
        return url


def classify_github_url(url: str) -> str:
    try:
        p = urlparse(url)
        path = p.path.lower()

        if p.netloc.startswith('raw.githubusercontent.com'):
            return 'raw'
        if url.endswith('.git'):
            return 'clone'
        if '/issues/' in path:
            return 'issue'
        if '/pull/' in path or '/pulls/' in path:
            return 'pull'
        if '/releases' in path:
            return 'release'

        parts = [x for x in path.split('/') if x]
        if len(parts) >= 2:
            return 'repo'

        return 'other'
    except Exception:
        return 'other'


def extract_urls_from_bytes(data: bytes) -> Set[str]:
    try:
        text = data.decode('utf-8', errors='ignore')
        return {normalize_url(u) for u in URL_RE.findall(text)}
    except Exception:
        return set()


def handle_file_bytes(data: bytes) -> None:
    urls = extract_urls_from_bytes(data)
    if not urls:
        return

    with lock:
        for u in urls:
            all_urls.add(u)
            if GITHUB_RE.search(u):
                git_urls.add(u)
                cat = classify_github_url(u)
                git_urls_classified[cat].add(u)


def process_regular_file(path: str) -> None:
    try:
        with open(path, 'rb') as f:
            handle_file_bytes(f.read())
    except Exception:
        pass


def process_zip(path: str) -> None:
    try:
        with zipfile.ZipFile(path) as z:
            for name in z.namelist():
                try:
                    handle_file_bytes(z.read(name))
                except Exception:
                    continue
    except Exception:
        pass


def process_tar(path: str) -> None:
    try:
        with tarfile.open(path, 'r:*') as t:
            for m in t.getmembers():
                if m.isfile():
                    try:
                        f = t.extractfile(m)
                        if f:
                            handle_file_bytes(f.read())
                    except Exception:
                        continue
    except Exception:
        pass


def process_tar_zst(path: str) -> None:
    if not zstd:
        return

    try:
        with open(path, 'rb') as f:
            dctx = zstd.ZstdDecompressor()
            stream = dctx.stream_reader(f)
            with tarfile.open(fileobj=stream, mode='r|*') as t:
                for m in t:
                    if m.isfile():
                        try:
                            f2 = t.extractfile(m)
                            if f2:
                                handle_file_bytes(f2.read())
                        except Exception:
                            continue
    except Exception:
        pass


def process_path(path: str) -> None:
    p = path.lower()

    if p.e