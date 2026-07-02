#!/data/data/com.termux/files/usr/bin/env python3
"""
Recursively deletes empty directories starting from the current directory.
Allows excluding specific directories from the deletion process.
"""

from pathlib import Path

# Folders to exclude (exact names)
EXCLUDED = {".git", "tmp", "var", ".cache", "etc"}


def delete_empty_dirs(root: Path) -> int:
    """
    Recursively deletes empty directories under the given root.
    Uses a post-order traversal to ensure nested empty directories are handled.

    Args:
        root (Path): The starting directory path.

    Returns:
        int: The number of directories deleted.
    """
    deleted_count = 0
    
    try:
        # Iterate through subdirectories
        for path in list(root.iterdir()):
            if path.is_dir():
                # Skip excluded folder names
                if path.name in EXCLUDED:
                    continue

                # Recurse first
                deleted_count += delete_empty_dirs(path)

                # After recursion, check if now empty
                try:
                    if not any(path.iterdir()):
                        print(f"Removing empty directory: {path}")
                        path.rmdir()
                        deleted_count += 1
                except PermissionError:
                    print(f"Permission denied: {path}")
                except OSError as e:
                    # Directory not empty or some other OS error
                    print(f"Could not remove {path}: {e}")
    except PermissionError:
        print(f"Permission denied accessing root: {root}")
    except OSError as e:
        print(f"Error accessing {root}: {e}")

    return deleted_count


if __name__ == "__main__":
    current_root = Path(".").resolve()
    print(f"Scanning for empty directories in: {current_root}")
    total_deleted = delete_empty_dirs(current_root)
    print(f"\nTotal empty directories removed: {total_deleted}")
