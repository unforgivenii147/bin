#!/usr/bin/env python3
"""
Deduplicates files by moving one copy per unique hash to a central store (~/dups)
and replacing all original copies (including the first one) with symlinks.
Supports restoration via a manifest file.
"""

import argparse
import json
import os
import shutil
import sys
from collections import defaultdict
from pathlib import Path

try:
    import xxhash
except ImportError:
    print("Error: 'xxhash' library is required. Install it with: pip install xxhash")
    sys.exit(1)

# Config
CACHE_PATH = Path.home() / ".cache" / "dups_xxhash_cache.json"
DUPS_DIR = Path.home() / "dups"
MANIFEST_PATH = DUPS_DIR / "manifest.json"
READ_CHUNK = 1 << 20  # 1 MiB


def load_json(path: Path) -> dict:
    """Loads a JSON file, returning an empty dict on failure."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_json(path: Path, data: dict) -> None:
    """Saves a dictionary to a JSON file, creating parent directories if needed."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving JSON to {path}: {e}")


def xxh64_of_path(p: Path) -> str:
    """Calculates the XXH64 hash of a file's content."""
    h = xxhash.xxh64()
    with p.open("rb") as f:
        while True:
            chunk = f.read(READ_CHUNK)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def build_groups(root: Path, cache: dict) -> dict:
    """
    Recursively scans the root directory and groups files by their content hash.
    Uses a cache to speed up repeated runs.
    """
    groups = defaultdict(list)
    for dirpath, _, filenames in os.walk(root):
        for name in filenames:
            fp = Path(dirpath) / name
            # ignore symlinks
            if fp.is_symlink():
                continue
            # only regular files
            try:
                st = fp.stat()
            except Exception:
                continue
            if not fp.is_file():
                continue
            
            key = str(fp.resolve())
            size = st.st_size
            mtime = st.st_mtime
            cached = cache.get(key)
            
            if cached and cached.get("size") == size and cached.get("mtime") == mtime:
                h = cached["hash"]
            else:
                try:
                    h = xxh64_of_path(fp)
                except Exception:
                    continue
                cache[key] = {"size": size, "mtime": mtime, "hash": h}
            groups[h].append(fp)
    return groups


def dedupe(root: Path, dry_run: bool = False) -> None:
    """
    Deduplicates files by moving them to DUPS_DIR and creating symlinks.
    """
    cache = load_json(CACHE_PATH) if CACHE_PATH.exists() else {}
    groups = build_groups(root, cache)
    save_json(CACHE_PATH, cache)

    DUPS_DIR.mkdir(parents=True, exist_ok=True)
    manifest = load_json(MANIFEST_PATH) if MANIFEST_PATH.exists() else {}
    changed = False

    for h, paths in groups.items():
        if len(paths) < 2 and not (DUPS_DIR / f"{h}__{paths[0].name}").exists():
            continue
        
        # sort to have deterministic choice of name for stored file
        paths_sorted = sorted(paths, key=lambda p: str(p))
        representative = paths_sorted[0]
        stored_name = f"{h}__{representative.name}"
        stored_path = DUPS_DIR / stored_name

        # If stored file doesn't exist, move one of the originals into dups
        if not stored_path.exists():
            if dry_run:
                print(f"[DRY] move: {representative} -> {stored_path}")
            else:
                shutil.move(str(representative), str(stored_path))
                print(f"moved: {representative} -> {stored_path}")
            changed = True
        
        # Replace ALL occurrences with symlinks (even the representative we just moved)
        for p in paths_sorted:
            if not p.exists() and not p.is_symlink():
                continue # Representative was moved, but we still need to symlink it
            
            if dry_run:
                print(f"[DRY] symlink: {p} -> {stored_path.resolve()}")
            else:
                if p.exists() or p.is_symlink():
                    try:
                        p.unlink()
                    except Exception as e:
                        print(f"Warning: could not remove {p}: {e}")
                        continue
                os.symlink(str(stored_path.resolve()), str(p))
                print(f"symlinked: {p} -> {stored_path}")
            changed = True

        # update manifest entry
        manifest_key = str(stored_path)
        if manifest_key not in manifest:
            manifest[manifest_key] = {"hash": h, "originals": []}
        
        for p in paths_sorted:
            p_str = str(p.resolve())
            if p_str not in manifest[manifest_key]["originals"]:
                manifest[manifest_key]["originals"].append(p_str)

    if not dry_run and changed:
        save_json(MANIFEST_PATH, manifest)
        save_json(CACHE_PATH, cache)
        print(f"Manifest updated at {MANIFEST_PATH}")


def restore(dry_run: bool = False) -> None:
    """
    Restores original files from DUPS_DIR based on the manifest.
    """
    if not MANIFEST_PATH.exists():
        print(f"No manifest found at {MANIFEST_PATH}")
        return
    
    manifest = load_json(MANIFEST_PATH)
    for stored_str, info in manifest.items():
        stored = Path(stored_str)
        if not stored.exists():
            print(f"Stored file missing: {stored}")
            continue
            
        originals = [Path(p) for p in info.get("originals", [])]
        for orig in originals:
            if orig.exists() and not orig.is_symlink():
                print(f"Skipping restore for {orig} (exists and not a symlink)")
                continue
            
            if dry_run:
                print(f"[DRY] restore {stored} -> {orig}")
            else:
                if orig.is_symlink():
                    orig.unlink()
                orig.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(stored, orig)
                print(f"Restored: {orig}")
        
        if dry_run:
            print(f"[DRY] remove stored file {stored}")
        else:
            stored.unlink()

    if not dry_run:
        MANIFEST_PATH.unlink()
        print("Restoration complete. Manifest removed.")


def main() -> None:
    """Main CLI entry point."""
    ap = argparse.ArgumentParser(description="Content-aware file deduplicator using symlinks.")
    ap.add_argument("path", nargs="?", default=".", help="Path to scan (default: current directory)")
    ap.add_argument("--dry-run", action="store_true", help="Show actions without making changes")
    ap.add_argument("--restore", action="store_true", help="Restore files from store")
    args = ap.parse_args()

    root = Path(args.path).resolve()
    if args.restore:
        restore(dry_run=args.dry_run)
    else:
        dedupe(root, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
