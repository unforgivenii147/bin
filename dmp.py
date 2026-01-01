#!/data/data/com.termux/files/usr/bin/env python3

from pathlib import Path

# Folders to exclude (exact names)
EXCLUDED = {'.git', 'tmp', 'var', '.cache'}


def delete_empty_dirs(root: Path) -> None:
    """Recursively delete empty directories under the given root."""
    # Iterate through subdirectories
    for path in list(root.iterdir()):
        if path.is_dir():
            # Skip excluded folder names
            if path.name in EXCLUDED:
                continue

            # Recurse first (post-order traversal)
            delete_empty_dirs(path)

            # After recursion, check if now empty
            try:
                # If directory is empty, remove it
                if not any(path.iterdir()):
                    print(f'Removing empty directory: {path}')
                    path.rmdir()
            except PermissionError:
                print(f'Permission denied: {path}')
            except OSError as e:
                # Directory not empty or some other OS error
                print(f'Could not remove {path}: {e}')


if __name__ == '__main__':
    root = Path('.').resolve()
    delete_empty_dirs(root)
