#!/usr/bin/env python3
"""
Recursive string search utility with archive support.
Features:
- Fast directory traversal (supports jwalk-based fastwalk).
- Search inside archives (zip, tar, whl, apk).
- Keyboard control to pause/resume (requires 'keyboard' module).
- Multi-threaded processing.
"""

import os
import argparse
import zipfile
import tarfile
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue
from pathlib import Path
import fnmatch

try:
    import fastwalk  # user-provided Rust-backed walker
except ImportError:
    fastwalk = None

# -------------------- Globals --------------------

pause_event = threading.Event()
pause_event.set()
results_queue = Queue()

DEFAULT_EXCLUDED_DIRS = {".git", "dist", "build", "target", "output", "__pycache__"}
DEFAULT_SKIPPED_EXTS = {".pyc", ".log", ".bak", ".pyo", ".so", ".pyd"}

ARCHIVE_EXTENSIONS = (".tar.gz", ".tar", ".tar.xz", ".tar.zst", ".tar.bz2", ".zip", ".whl", ".apk")

# -------------------- Keyboard --------------------


def setup_keyboard_listener() -> bool:
    """
    Sets up a keyboard listener for pausing and resuming the search.
    Requires the 'keyboard' library to be installed.
    """
    try:
        import keyboard

        def on_key_press(event):
            if event.name in ("space", "p") and pause_event.is_set():
                pause_event.clear()
                print("\n[PAUSED] Press 'c' to continue...")
            elif event.name == "c" and not pause_event.is_set():
                pause_event.set()
                print("\n[RESUMED] Searching...")

        keyboard.on_press(on_key_press)
        return True
    except ImportError:
        # Silently fail if keyboard is not installed
        return False


# -------------------- Helpers --------------------


def is_excluded(path: Path, excluded_dirs: set, excluded_patterns: set) -> bool:
    """
    Checks if a given path should be excluded based on directory names or glob patterns.
    """
    for part in path.parts:
        if part in excluded_dirs:
            return True
    for pattern in excluded_patterns:
        if fnmatch.fnmatch(path.name, pattern):
            return True
    return False


def should_skip_file(path: Path) -> bool:
    """
    Returns True if the file extension is in the default skipped list.
    """
    return path.suffix in DEFAULT_SKIPPED_EXTS


def report_result(file_path: str, line_num: int = None) -> None:
    """
    Prints a found result and adds it to the results queue.
    """
    if line_num:
        print(f"[FOUND] {file_path} (Line: {line_num})")
    else:
        print(f"[FOUND] {file_path}")
    results_queue.put((file_path, line_num))


# -------------------- Search Logic --------------------


def search_in_file(file_path: Path, search_string: str, search_content: bool) -> list:
    """
    Searches for the search_string in a file's name or its content.
    Returns a list of (path, line_number) tuples.
    """
    pause_event.wait()
    results = []

    if not search_content:
        if search_string.lower() in file_path.name.lower():
            results.append((str(file_path), None))
        return results

    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            for ln, line in enumerate(f, 1):
                pause_event.wait()
                if search_string in line:
                    results.append((str(file_path), ln))
    except Exception:
        pass

    return results


def extract_and_search_archive(archive_path: Path, search_string: str, search_content: bool) -> list:
    """
    Opens an archive and searches for the search_string in member names or content.
    """
    results = []

    try:
        if archive_path.suffix == ".zip" or archive_path.name.endswith((".whl", ".apk")):
            with zipfile.ZipFile(archive_path) as zf:
                for member in zf.namelist():
                    pause_event.wait()
                    ref = f"{archive_path}::{member}"

                    if not search_content:
                        if search_string.lower() in member.lower():
                            results.append((ref, None))
                    else:
                        try:
                            with zf.open(member) as f:
                                for ln, line in enumerate(f, 1):
                                    try:
                                        decoded_line = line.decode("utf-8", errors="ignore")
                                        if search_string in decoded_line:
                                            results.append((ref, ln))
                                    except Exception:
                                        continue
                        except Exception:
                            pass

        else:
            with tarfile.open(archive_path, "r:*") as tf:
                for m in tf.getmembers():
                    pause_event.wait()
                    if not m.isfile():
                        continue

                    ref = f"{archive_path}::{m.name}"

                    if not search_content:
                        if search_string.lower() in m.name.lower():
                            results.append((ref, None))
                    else:
                        try:
                            f = tf.extractfile(m)
                            if f:
                                for ln, line in enumerate(f, 1):
                                    try:
                                        decoded_line = line.decode("utf-8", errors="ignore")
                                        if search_string in decoded_line:
                                            results.append((ref, ln))
                                    except Exception:
                                        continue
                        except Exception:
                            pass
    except Exception:
        pass

    return results


def process_file(path: Path, search_string: str, search_content: bool) -> None:
    """
    Dispatches a file to either archive search or regular file search.
    """
    if path.name.lower().endswith(ARCHIVE_EXTENSIONS):
        results = extract_and_search_archive(path, search_string, search_content)
    else:
        results = search_in_file(path, search_string, search_content)

    for r in results:
        report_result(*r)


# -------------------- Main --------------------


def main() -> None:
    """
    Main entry point for fdrg. Parses arguments and initiates multi-threaded search.
    """
    parser = argparse.ArgumentParser(description="Fast recursive string search")
    parser.add_argument("search_string", help="String to search for")
    parser.add_argument("-c", "--content", action="store_true", help="Search in file content instead of filename")
    parser.add_argument("-d", "--directory", default=".", help="Root directory to start search")
    parser.add_argument("-o", "--output", default="output", help="Output identifier (not currently used for file output)")
    parser.add_argument("--exclude", action="append", default=[], help="Exclude directory or glob pattern (repeatable)")
    parser.add_argument("-w", "--workers", type=int, default=8, help="Number of worker threads")

    args = parser.parse_args()

    excluded_dirs = DEFAULT_EXCLUDED_DIRS | {e for e in args.exclude if not any(ch in e for ch in "*?[]")}
    excluded_patterns = {e for e in args.exclude if any(ch in e for ch in "*?[]")}

    setup_keyboard_listener()

    root = Path(args.directory).resolve()
    print(f"[INFO] Root: {root}")
    print(f"[INFO] Mode: {'content' if args.content else 'filename'}")
    print(f"[INFO] Excluded dirs: {sorted(excluded_dirs)}")
    print(f"[INFO] Excluded patterns: {sorted(excluded_patterns)}")
    print("=" * 80)

    files = []
    
    if fastwalk:
        walker = fastwalk.walk(root, follow_symlinks=False)
        for entry in walker:
            path = Path(entry.path)
            if entry.is_dir:
                continue
            if should_skip_file(path) or is_excluded(path, excluded_dirs, excluded_patterns):
                continue
            files.append(path)
    else:
        # Fallback to os.walk if fastwalk is not available
        for r, dirs, filenames in os.walk(root):
            # Prune excluded dirs
            dirs[:] = [d for d in dirs if d not in excluded_dirs]
            for f in filenames:
                path = Path(r) / f
                if should_skip_file(path) or is_excluded(path, excluded_dirs, excluded_patterns):
                    continue
                files.append(path)

    print(f"[INFO] Files queued: {len(files)}\n")

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futures = [ex.submit(process_file, p, args.search_string, args.content) for p in files]
        for f in as_completed(futures):
            # Results are reported via report_result and results_queue
            pass

    print(f"[INFO] Total results: {results_queue.qsize()}")


if __name__ == "__main__":
    main()
