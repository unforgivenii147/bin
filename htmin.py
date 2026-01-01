#!/data/data/com.termux/files/usr/bin/env python3

import htmlmin


def minify_html_in_directory(root_dir='.') -> None:
    """Recursively finds all HTML files (.html or .htm) in the given directory
    and minifies them in-place, overwriting the original files.
    """
    minified_count = 0
    errors_count = 0
    # os.walk iterates through directories recursively
    for foldername, _subfolders, filenames in os.walk(root_dir):
        for filename in filenames:
            # Check for common HTML extensions
            if filename.endswith(('.html', '.htm')):
                file_path = os.path.join(foldername, filename)
                try:
                    # 1. Read the original HTML content
                    with pathlib.Path(file_path).open(encoding='utf-8') as f:
                        html_content = f.read()
                    # 2. Minify the content
                    minified_content = htmlmin.minify(
                        html_content,
                        remove_comments=True,
                        remove_empty_space=True,
                        reduce_empty_attributes=True,
                        # Set to False if you have inline JS/CSS you want to preserve fully
                        # True often results in better minification.
                        do_not_minify_json_script=False,
                    )
                    # 3. Overwrite the original file (in-place)
                    with pathlib.Path(file_path).open('w',
                                                      encoding='utf-8') as f:
                        f.write(minified_content)
                    minified_count += 1
                except Exception:
                    errors_count += 1


if __name__ == '__main__':
    # Start the process in the current working directory
    minify_html_in_directory(pathlib.Path.cwd())
