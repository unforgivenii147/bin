#!/usr/bin/env python3
import sys


def sort_uniq_inplace(fname):
    with open(fname, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # strip trailing newlines, deduplicate, sort
    unique_sorted = sorted(set(line.rstrip('\n') for line in lines))

    # write back with newline
    with open(fname, 'w', encoding='utf-8') as f:
        for line in unique_sorted:
            f.write(line + '\n')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f'Usage: {sys.argv[0]} <filename>')
        sys.exit(1)

    sort_uniq_inplace(sys.argv[1])
