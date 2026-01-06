#!/usr/bin/env python3
"""
File translator script that:
1. Reads a file and auto-detects language
2. Translates to English in chunks respecting word boundaries
3. Respects 5000 character limit per request
4. Saves result to fname_en.extension
5. Skips if output file already exists
"""

import os
import sys
import time
from pathlib import Path

from deep_translator import GoogleTranslator
from tqdm import tqdm

MAX_CHARS = 5000  # Character limit per request


def get_output_filename(input_file):
    """Generate output filename:  fname_en.extension"""
    path = Path(input_file)
    stem = path.stem
    suffix = path.suffix
    return path.parent / f'{stem}_en{suffix}'


def load_file(input_file):
    """Load file content with encoding detection."""
    encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']

    for encoding in encodings:
        try:
            with open(input_file, 'r', encoding=encoding) as f:
                return f.read()
        except (UnicodeDecodeError, IOError):
            continue

    raise IOError(f'Could not read file {input_file} with any encoding')


def save_file(output_file, content):
    """Save content to file."""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)


def find_chunk_boundary(text, max_chars):
    """
    Find a good chunk boundary respecting word boundaries.
    Tries to split at the last space before max_chars limit.
    """
    if len(text) <= max_chars:
        return len(text)

    # Try to find last space/newline before limit
    search_area = text[:max_chars]

    # Priority order for breaking points
    for delimiter in ['\n', '\r\n', '.  ', '!  ', '?  ', '; ', ', ', ' ']:
        last_pos = search_area.rfind(delimiter)
        if last_pos > 0:
            return last_pos + len(delimiter)

    # If no delimiter found, break at last space
    last_space = search_area.rfind(' ')
    if last_space > 0:
        return last_space + 1

    # If still no space, just break at limit (shouldn't happen often)
    return max_chars


def chunk_text(text, max_chars):
    """
    Split text into chunks respecting word boundaries and character limit.
    """
    chunks = []
    pos = 0

    while pos < len(text):
        remaining = text[pos:]

        if len(remaining) <= max_chars:
            chunks.append(remaining)
            break

        # Find good break point
        chunk_end = find_chunk_boundary(remaining, max_chars)
        chunks.append(remaining[:chunk_end])
        pos += chunk_end

    return chunks


def translate_chunk(text, source_lang='auto'):
    """Translate a single chunk with retry."""
    for attempt in range(3):
        try:
            translator = GoogleTranslator(source=source_lang, target='en')
            translated = translator.translate(text)
            return translated, source_lang
        except Exception as e:
            print(f'[WARN] Translation failed (attempt {attempt + 1}/3): {e}')
            time.sleep(1 + attempt)

    raise Exception(f'Failed to translate chunk after 3 attempts')


def translate_file(input_file, source_lang='auto'):
    """
    Translate entire file, chunking if necessary.
    """
    print(f'[INFO] Reading file: {input_file}')
    content = load_file(input_file)
    content_length = len(content)
    print(f'[INFO] File size: {content_length} characters')

    # Check if chunking needed
    if content_length <= MAX_CHARS:
        print(f'[INFO] Content fits in single request ({content_length} chars)')
        print(f'[INFO] Translating...')
        translated, detected_lang = translate_chunk(content, source_lang)
        print(f'[INFO] Detected language: {detected_lang}')
        return translated

    # Need to chunk
    chunks = chunk_text(content, MAX_CHARS)
    total_chunks = len(chunks)
    print(f'[INFO] Content split into {total_chunks} chunks')
    print(f'[INFO] Chunk sizes: {[len(c) for c in chunks]}')

    translated_chunks = []
    detected_lang = None
    pbar = tqdm(total=total_chunks, desc='Translating', unit='chunk')

    try:
        for i, chunk in enumerate(ch