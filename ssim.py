#!/usr/bin/env python
import os
import shutil
import sys
import argparse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import xxhash
import ssdeep
from tqdm import tqdm
from collections import defaultdict


class FileSimilarityDetector:

    def __init__(self, root_dir='.', exclude_dirs=None):
        self.root_dir = Path(root_dir)
        self.exclude_dirs = exclude_dirs or [
            '.git', '__pycache__', 'node_modules'
        ]
        self.file_data = {}  # Stores {path: (xxhash, ssdeep_hash)}
        self.duplicates = defaultdict(list)  # Stores {xxhash: [path1, path2]}

    def scan_files(self):
        files = []
        for root, dirs, filenames in os.walk(self.root_dir):
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]
            for filename in filenames:
                files.append(Path(root) / filename)
        return files

    def calculate_hashes(self, filepath):
        """Calculate both xxhash (duplicates) and ssdeep (similarity)."""
        try:
            with open(filepath, 'rb') as f:
                content = f.read()
                # xxhash for 100% identity
                xh = xxhash.xxh64(content).hexdigest()
                # ssdeep for fuzzy similarity
                sh = ssdeep.hash(content)
                return str(filepath), xh, sh
        except Exception as e:
            return str(filepath), None, None

    def process_all_files(self, files):
        print(f'Processing {len(files)} files...')
        with ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(self.calculate_hashes, f) for f in files
            ]
            for future in tqdm(as_completed(futures),
                               total=len(files),
                               desc='Hashing'):
                path, xh, sh = future.result()
                if xh and sh:
                    self.file_data[path] = {'xxhash': xh, 'ssdeep': sh}
                    self.duplicates[xh].append(path)

        # Filter duplicates: only keep entries with > 1 file
        self.duplicates = {
            k: v
            for k, v in self.duplicates.items() if len(v) > 1
        }
        return self.file_data

    def create_similarity_groups(self, threshold=50):
        """Groups files that are similar but NOT identical."""
        # We only look at one 'representative' from each duplicate set to avoid redundancy
        unique_files = []
        already_accounted_for = set()

        # Flatten all duplicates to exclude them from similarity grouping
        for dup_list in self.duplicates.values():
            already_accounted_for.update(dup_list)

        # Get files that are NOT duplicates
        files_to_compare = [
            p for p in self.file_data.keys() if p not in already_accounted_for
        ]

        visited = set()
        groups = []

        for i, file1 in enumerate(
                tqdm(files_to_compare, desc='Finding Similarities')):
            if file1 in visited:
                continue

            group = [file1]
            visited.add(file1)
            hash1 = self.file_data[file1]['ssdeep']

            for file2 in files_to_compare[i + 1:]:
                if file2 in visited:
                    continue

                score = ssdeep.compare(hash1, self.file_data[file2]['ssdeep'])
                if score >= threshold:
                    group.append(file2)
                    visited.add(file2)

            if len(group) > 1:
                groups.append(group)
        return groups

    def export_files(self, groups, mode='copy', output_dir='output'):
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        action = shutil.move if mode == 'move' else shutil.copy2
        verb = 'Moving' if mode == 'move' else 'Copying'

        for idx, group in enumerate(groups, 1):
            group_dir = output_path / f'similarity_group_{idx}'
            group_dir.mkdir(exist_ok=True)
            for filepath in group:
                try:
                    src = Path(filepath)
                    action(src, group_dir / src.name)
                except Exception as e:
                    print(f'Error processing {filepath}: {e}')


def main():
    parser = argparse.ArgumentParser(
        description='Detect duplicates and similar files.')
    parser.add_argument('threshold',
                        type=int,
                        help='Similarity threshold (0-100)')
    parser.add_argument('-m',
                        '--move',
                        action='store_true',
                        help='Move files instead of copying')
    parser.add_argument('-o',
                        '--output',
                        default='output',
                        help='Output directory')
    args = parser.parse_args()

    detector = FileSimilarityDetector()
    files = detector.scan_files()

    if not files:
        print('No files found.')
        return

    detector.process_all_files(files)

    # Handle Similarity Groups
    sim_groups = detector.create_similarity_groups(args.threshold)
    if sim_groups:
        mode_str = 'move' if args.move else 'copy'
        detector.export_files(sim_groups,
                              mode=mode_str,
                              output_dir=args.output)
        print(f'Processed {len(sim_groups)} similarity groups.')
    else:
        print('No similar (non-identical) files found.')

    # Final Report on Duplicates
    if detector.duplicates:
        print('\n' + '=' * 30)
        print('!!! DUPLICATES FOUND !!!')
        print(
            'The following sets of files are 100% identical (excluded from similarity groups):'
        )
        for xh, paths in detector.duplicates.items():
            print(f'\nHash: {xh}')
            for p in paths:
                print(f'  - {p}')
        print('=' * 30)


if __name__ == '__main__':
    main()
