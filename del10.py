#!/data/data/com.termux/files/usr/bin/env python3

import sys

if len(sys.argv) != 2:
    print("Usage: python script.py <filename>")
    sys.exit(1)

fname = sys.argv[1]

try:
    with open(fname) as f:
        lines = f.readlines()

    # Keep only lines with >= 10 characters (excluding surrounding whitespace)
    filtered = [line for line in lines if len(line.strip()) >= 30]

    with open(fname, "w") as f:
        f.writelines(filtered)

except FileNotFoundError:
    print(f"Error: File '{fname}' not found.")
except Exception as e:
    print("An error occurred:", e)
