#!/usr/bin/env python3
# file: move_binary_files.py

import shutil
from pathlib import Path


def is_binary(file_path: Path, blocksize: int = 1024) -> bool:
    """Check if a file is binary by reading a small portion."""
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(blocksize)
            if not chunk:
                return False  # empty file is considered non-binary
            # If it contains null bytes or non-text bytes, treat as binary
            text_chars = bytearray({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)))
            return bool(chunk.translate(None, text_chars))
    except Exception:
        return False


def main():
    current_dir = Path.cwd()
    binary_dir = current_dir / 'binary'
    binary_dir.mkdir(exist_ok=True)

    files_moved = 0
    for f in current_dir.iterdir():
        if f.is_file() and is_binary(f):
            try:
                shutil.move(str(f), binary_dir / f.name)
                print(f'Moved: {f.name} -> binary/{f.name}')
                files_moved += 1
            except Exception as e:
                print(f'Failed to move {f.name}: {e}')

    if files_moved == 0:
        print('No binary files found to move.')
    else:
        print(f'Total binary files moved: {files_moved}')


if __name__ == '__main__':
    main()
