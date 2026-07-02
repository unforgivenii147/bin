#!/data/data/com.termux/files/usr/bin/python
"""
Generate a requirements file with unpinned package versions.

This module runs 'pip freeze' and extracts only the package names,
effectively unpinning the versions for a cleaner requirements file.
"""

import subprocess
import sys
from typing import List
from pathlib import Path


def create_unpinned_requirements(output_file: str = "req.txt") -> None:
    """
    Run pip freeze and save only package names to the specified output file.

    Args:
        output_file: The name of the file to save the package names to.
    """
    try:
        # Run pip freeze and capture output
        result = subprocess.run(
            ["pip", "freeze"], capture_output=True, text=True, check=True
        )

        # Process lines: split at common delimiters and take the package name
        # Delimiters: == (standard), >=, <=, ~= (specifiers), @ (direct links/URLs)
        package_names: List[str] = []
        for line in result.stdout.splitlines():
            line = line.strip()
            if not line or line.startswith(("#", "-e ")):
                # Skip comments and editable installs that we might not want to simplify
                # Or handle editable installs separately if needed.
                # Here we just keep the base name if possible.
                if line.startswith("-e "):
                    line = line[3:].strip()
                else:
                    continue

            # Split at the first occurrence of any version/link operator
            # Using partition to safely split at the first occurrence
            pkg = line
            for op in ["==", ">=", "<=", "~=", " @ ", ">", "<", "!="]:
                if op in pkg:
                    pkg = pkg.split(op)[0].strip()
            
            if pkg:
                package_names.append(pkg)

        # Remove duplicates while preserving order
        seen = set()
        unique_packages = [p for p in package_names if not (p in seen or seen.add(p))]

        # Save to file
        path = Path(output_file)
        path.write_text("\n".join(unique_packages) + "\n", encoding="utf-8")

        print(f"Successfully saved {len(unique_packages)} package names to {output_file}.")

    except subprocess.CalledProcessError as e:
        print(f"Error running pip freeze: {e}", file=sys.stderr)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)


if __name__ == "__main__":
    out_file = sys.argv[1] if len(sys.argv) > 1 else "req.txt"
    create_unpinned_requirements(out_file)
