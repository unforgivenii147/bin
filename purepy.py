#!/data/data/com.termux/files/usr/bin/env python3

import sys

import requests


def has_native_wheels(info) -> bool:
    urls = info.get('urls', [])
    for u in urls:
        filename = u.get('filename', '').lower()
        if any(
            ext in filename for ext in ['.so', '.pyd', '.dll', 'win_amd64', 'manylinux', 'macosx']
        ):
            return True
    return False


def check_package(name) -> str:
    url = f'https://pypi.org/pypi/{name}/json'
    resp = requests.get(url)
    if resp.status_code != 200:
        return 'not_found'
    with open(str(name) + '.json', 'w') as fo:
        fo.write(str(resp.json()))

    info = resp.json()
    if has_native_wheels(info):
        print(f'{name} is not pure')
        return 'native'
    print(f'{name} is pure python')
    return 'pure'


def main() -> None:
    if len(sys.argv) < 2:
        print('Usage: python detect_pure_python.py <package_list.txt>')
        sys.exit(1)

    infile = sys.argv[1]

    pure = []
    native = []
    missing = []

    with open(infile) as f:
        for line in f:
            pkg = line.strip()
            if not pkg:
                continue
            result = check_package(pkg)
            if result == 'pure':
                pure.append(pkg)
            elif result == 'native':
                native.append(pkg)
            else:
                missing.append(pkg)

    with open('pure_python.txt', 'w') as f:
        f.write('\n'.join(sorted(set(pure))))

    with open('native_extensions.txt', 'w') as f:
        f.write('\n'.join(sorted(set(native))))

    with open('not_found.txt', 'w') as f:
        f.write('\n'.join(sorted(set(missing))))

    print('Done!')
    print(f'Pure Python: {len(pure)}')
    print(f'Native-required: {len(native)}')
    print(f'Not found: {len(missing)}')


if __name__ == '__main__':
    main()
