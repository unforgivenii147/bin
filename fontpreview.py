#!/data/data/com.termux/files/usr/bin/env python3

import os
import pathlib

FONT_EXTENSIONS = ('.ttf', '.otf', '.woff', '.woff2', '.eot', '.svg')
OUTPUT_HTML = 'fonts_preview.html'
FONT_SIZES = [22]


def find_fonts(root_dir='.'):
    fonts = []
    for dirpath, _, filenames in os.walk(root_dir):
        fonts.extend(
            os.path.join(dirpath, filename)
            for filename in filenames
            if filename.lower().endswith(FONT_EXTENSIONS)
        )
    return fonts


def generate_html(font_files):
    html = [
        '<!DOCTYPE html>',
        "<html lang='en'>",
        '<head>',
        "<meta charset='UTF-8'>",
        '<title>Font Preview</title>',
        '<style>',
        "body { font-family: 'fontello.woff2'; src: url('./fonts/fontello.woff2'); padding: 14px; }",
        ".font-preview { font-family: 'fontello.woff2'; src: url('./fonts/fontello.woff2'); margin-bottom: 50px; }",
        ".h2 {font-family: 'fontello.woff2'; src: url('./fonts/fontello.woff2');}",
        '</style>',
        '</head>',
        '<body>',
        '<h1>Font Preview</h1>',
    ]
    for font_path in font_files:
        font_name = pathlib.Path(font_path).name
        html.append("<div class='font-preview'>")
#        html.append(f'<h2>{font_name}</h2>')
        # Embed font using @font-fac
        html.append('<style>')
        html.append(
            f"@font-face {{ font-family: '{font_name}'; src: url('{font_path}'); }}",
        )
        html.append('</style>')
        html.extend(
            f'<p style=\'font-family: "{font_name}"; font-size: {size}px;\'>({font_path})</p>'
            for size in FONT_SIZES
        )
        html.append('</div>')
    html.append('</body></html>')
    return '\n'.join(html)


def main() -> None:
    fonts = find_fonts()
    if not fonts:
        return
    html_content = generate_html(fonts)
    with pathlib.Path(OUTPUT_HTML).open('w', encoding='utf-8') as f:
        f.write(html_content)

    print('font-preview.html created.')


if __name__ == '__main__':
    main()
