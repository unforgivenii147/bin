#!/usr/bin/env python3
"""Adds command aliases for uutils-coreutils to the .bash_aliases file.

This script checks for a list of 'uu-' commands and adds them as aliases
(without the 'uu-' prefix) to the user's ~/.bash_aliases file, ensuring
no duplicate aliases are added.
"""

import os
from pathlib import Path
from typing import List, Set

COMMANDS = [
    "uu-arch", "uu-b2sum", "uu-base32", "uu-base64", "uu-basename",
    "uu-basenc", "uu-cat", "uu-chgrp", "uu-chmod", "uu-chown", "uu-chroot",
    "uu-cksum", "uu-comm", "uu-coreutils", "uu-cp", "uu-csplit", "uu-cut",
    "uu-date", "uu-dd", "uu-df", "uu-dir", "uu-dircolors", "uu-dirname",
    "uu-du", "uu-echo", "uu-env", "uu-expand", "uu-expr", "uu-factor",
    "uu-false", "uu-fmt", "uu-fold", "uu-groups", "uu-hashsum", "uu-head",
    "uu-hostname", "uu-id", "uu-install", "uu-join", "uu-kill", "uu-link",
    "uu-ln", "uu-logname", "uu-ls", "uu-md5sum", "uu-mkdir", "uu-mkfifo",
    "uu-mknod", "uu-mktemp", "uu-more", "uu-mv", "uu-nice", "uu-nl",
    "uu-nohup", "uu-nproc", "uu-numfmt", "uu-od", "uu-paste", "uu-pathchk",
    "uu-pr", "uu-printenv", "uu-printf", "uu-ptx", "uu-pwd", "uu-readlink",
    "uu-realpath", "uu-rm", "uu-rmdir", "uu-seq", "uu-sha1sum", "uu-sha224sum",
    "uu-sha256sum", "uu-sha384sum", "uu-sha512sum", "uu-shred", "uu-shuf",
    "uu-sleep", "uu-sort", "uu-split", "uu-stat", "uu-stdbuf", "uu-stty",
    "uu-sum", "uu-sync", "uu-tac", "uu-tail", "uu-tee", "uu-test",
    "uu-timeout", "uu-touch", "uu-tr", "uu-true", "uu-truncate", "uu-tsort",
    "uu-tty", "uu-uname", "uu-unexpand", "uu-uniq", "uu-unlink", "uu-vdir",
    "uu-wc", "uu-whoami", "uu-yes",
]


def get_existing_aliases(file_path: Path) -> Set[str]:
    """Reads the existing aliases from the given file.

    Args:
        file_path: The path to the aliases file.

    Returns:
        A set of existing alias names found in the file.
    """
    if not file_path.exists():
        return set()

    aliases = set()
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("alias "):
                    # Extract the alias name (e.g., 'ls' from 'alias ls="uu-ls"')
                    parts = line.split("=", 1)
                    if parts:
                        alias_name = parts[0].replace("alias ", "").strip()
                        aliases.add(alias_name)
    except OSError:
        pass
    return aliases


def main() -> None:
    """Main function to add missing aliases to ~/.bash_aliases."""
    aliases_file = Path("~/.bash_aliases").expanduser()
    existing_aliases = get_existing_aliases(aliases_file)

    to_add: List[str] = []
    for cmd in COMMANDS:
        alias_name = cmd.replace("uu-", "")
        if alias_name not in existing_aliases:
            to_add.append(f'alias {alias_name}="{cmd}"\n')

    if to_add:
        try:
            with open(aliases_file, "a", encoding="utf-8") as f:
                f.writelines(to_add)
            print(f"✅ Added {len(to_add)} aliases to {aliases_file}")
        except OSError as e:
            print(f"❌ Error writing to {aliases_file}: {e}")
    else:
        print(f"✨ All aliases already exist in {aliases_file}")


if __name__ == "__main__":
    main()
