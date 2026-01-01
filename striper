#!/data/data/com.termux/files/usr/bin/env python3

import sys


def remove_spaces_from_file(fname) -> None:
    try:
        with open(fname) as file:
            lines = file.readlines()

        # Strip leading and trailing spaces from each line
        cleaned_lines = [line.strip() for line in lines]

        # Optionally, write the cleaned lines back to the file or print
        with open(fname, 'w') as file:
            file.writelines('\n'.join(cleaned_lines))

        print(f"Spaces removed successfully from '{fname}'")

    except FileNotFoundError:
        print(f"Error: File '{fname}' not found.")
    except Exception as e:
        print(f'An error occurred: {e}')


if __name__ == '__main__':
    # Ensure the script is called with the correct argument
    if len(sys.argv) != 2:
        print('Usage: python remove_spaces.py <filename>')
    else:
        filename = sys.argv[1]
        remove_spaces_from_file(filename)
