#!/data/data/com.termux/files/usr/bin/env python3

import os
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed

EXCLUDE_DIRS = {'.git', '__pycache__'}
EXCLUDED_EXT = {'.whl', '.zip', '.tar.gz', '.gz', '.tar.xz', '.7z'}


def is_binary(path) -> bool:
    """Return True if file is binary by checking for null bytes."""
    try:
        with open(path, 'rb') as f:
            chunk = f.read(4096)
            if b'\0' in chunk:
                return True
    except:
        return True
    return False


def load_patterns_from_file(path='/sdcard/all.xtx'):
    """Reads patterns, filters length, and updates the file with unique entries."""
    if not os.path.exists(path):
        raise FileNotFoundError(f'{path} not found')

    with open(path, encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # Split by triple newline as per original logic
    raw_groups = [block.strip() for block in content.split('\n\n\n')]

    # Filter out empty or short patterns
    patterns = [g for g in raw_groups if g and len(g) >= 5]
    unique_patterns = list(set(patterns))

    # Overwrite with filtered set
    with open(path, 'w', encoding='utf-8') as fo:
        for gg in unique_patterns:
            fo.write(gg + '\n\n\n')

    print(f'Filtered out {len(raw_groups) - len(unique_patterns)} short or duplicate patterns')
    return unique_patterns


def process_file(path, patterns) -> str | None:
    """Worker function: Performs the string replacement."""
    if is_binary(path):
        return f'Skipping binary: {path}'

    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            data = f.read()
    except Exception as e:
        return f'ERROR reading {path}: {e}'

    new_data = data
    for p in patterns:
        if p in new_data:
            new_data = new_data.replace(p, '')

    if new_data != data:
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_data)
            return f'Cleaned: {path}'
        except Exception as e:
            return f'ERROR writing {path}: {e}'

    return None


def collect_files(root):
    """Collect text-like files to process in parallel."""
    files = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]

        for fname in filenames:
            if fname == 'all.xtx':
                continue
            if any(fname.endswith(ext) for ext in EXCLUDED_EXT):
                continue

            full = os.path.join(dirpath, fname)
            files.append(full)
    return files


def clean_dir_concurrent(root, patterns) -> None:
    files = collect_files(root)
    print(f'Found {len(files)} candidate files')

    # Using ProcessPoolExecutor for CPU-bound string replacement tasks
    with ProcessPoolExecutor() as executor:
        # Map patterns to every file path for the worker
        future_to_file = {executor.submit(process_file, f, patterns): f for f in files}

        for future in as_completed(future_to_file):
            result = future.result()
            if result:
                print(result)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(
        description='Remove strings from text files recursively (Concurrent)'
    )
    ap.add_argument('--path', default='.', help='Directory to clean')
    ap.add_argument(
        '--file',
        default='/sdcard/all.xtx',
        help='File containing patterns separated by empty lines',
    )
    args = ap.parse_args()

    try:
        patterns_list = load_patterns_from_file(args.file)
        print(f'Loaded {len(patterns_list)} usable patterns from {args.file}')
        clean_dir_concurrent(args.path, patterns_list)
    except Exception as e:
        print(f'Fatal Error: {e}')
