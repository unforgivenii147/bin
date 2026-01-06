#!/usr/bin/env python3
import argparse
import datetime
import grp
import os
import pwd
import stat
import sys
from pathlib import Path

# =============================
# ANSI COLORS
# =============================

COLORS = {
    'dir': '\033[34m',
    'link': '\033[36m',
    'exec': '\033[32m',
    'reset': '\033[0m',
}


def use_color(mode: str) -> bool:
    if mode == 'always':
        return True
    if mode == 'never':
        return False
    return sys.stdout.isatty()


def colorize(name, st, enabled):
    if not enabled:
        return name
    if stat.S_ISDIR(st.st_mode):
        return f'{COLORS["dir"]}{name}{COLORS["reset"]}'
    if stat.S_ISLNK(st.st_mode):
        return f'{COLORS["link"]}{name}{COLORS["reset"]}'
    if st.st_mode & stat.S_IXUSR:
        return f'{COLORS["exec"]}{name}{COLORS["reset"]}'
    return name


# =============================
# HELPERS
# =============================


def human_size(size):
    for unit in ('B', 'K', 'M', 'G', 'T'):
        if size < 1024:
            return f'{size}{unit}'
        size //= 1024
    return f'{size}P'


def indicator(path, st):
    if stat.S_ISDIR(st.st_mode):
        return '/'
    if stat.S_ISLNK(st.st_mode):
        return '@'
    if st.st_mode & stat.S_IXUSR:
        return '*'
    return ''


def format_time(ts, full):
    dt = datetime.datetime.fromtimestamp(ts)
    return dt.strftime('%Y-%m-%d %H:%M:%S' if full else '%b %d %H:%M')


# =============================
# ENTRY FORMAT
# =============================


def format_entry(entry, args, color_enabled):
    try:
        st = entry.stat(follow_symlinks=args.L)
    except FileNotFoundError:
        return ''

    name = entry.name
    name = colorize(name, st, color_enabled)

    if args.p and entry.is_dir():
        name += '/'
    if args.F:
        name += indicator(entry, st)

    inode = f'{st.st_ino} ' if args.i else ''
    blocks = f'{st.st_blocks} ' if args.s else ''

    if not args.l:
        return f'{inode}{blocks}{name}'

    perms = stat.filemode(st.st_mode)
    nlink = st.st_nlink
    uid = st.st_uid if args.n else pwd.getpwuid(st.st_uid).pw_name
    gid = st.st_gid if args.n else grp.getgrgid(st.st_gid).gr_name
    size = human_size(st.st_size) if args.h else st.st_size

    ts = st.st_ctime if args.lc else st.st_atime if args.lu else st.st_mtime

    time_str = format_time(ts, args.full_time)

    return f'{inode}{blocks}{perms} {nlink} {uid} {gid} {size:>6} {time_str} {name}'


# =============================
# DIRECTORY SCAN
# =============================


def scan_dir(path, args):
    try:
        with os.scandir(path) as it:
            entries = [Path(e.path) for e in it]
    except PermissionError:
        print(f"ls: cannot open directory '{path}'", file=sys.stderr)
        return []

    if not args.a:
        if args.A:
            entries = [
                e for e in entries if e.name not in ('.', '..') and not e.name.startswith('.')
            ]
        else:
            entries = [e for e in entries if not e.name.startswith('.')]

    def key(p):
        try:
            st = p.stat(follow_symlinks=args.L)
        except FileNotFoundError:
            return 0
        if args.S:
            return -st.st_size
        if args.t:
            return -st.st_mtime
        if args.tc:
            return -st.st_ctime
        if args.tu:
            return -st.st_atime
        if args.X:
            return p.suffix
        return p.name

    entries.sort(key=key, reverse=args.r)

    if args.group_directories_first:
        entries.sort(key=lambda e: not e.is_dir())

    return entries


# =============================
# COLUMN OUTPUT
# =============================


def print_columns(items, width, by_row):
    if not items:
        return

    max_len = max(len(i) for i in items) + 2
    cols = max(1, width // max_len)
    rows = (len(items) + cols - 1) // cols

    for r in range(rows):
        for c in range(cols):
            idx = r * cols + c if by_row else c * rows + r
            if idx < len(items):
                print(items[idx].ljust(max_len), end='')