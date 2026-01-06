#!/data/data/com.termux/files/usr/bin/env python3

import sys

import pytesseract
from PIL import Image, ImageFilter, ImageOps


def preprocess_image(img):
    # Convert to grayscale
    img = img.convert('L')
    # Increase contrast
    img = ImageOps.autocontrast(img)
    # Reduce noise
    img = img.filter(ImageFilter.MedianFilter(size=3))
    # Binarize (simple threshold)
    threshold = 150
    return img.point(lambda x: 255 if x > threshold else 0)


def extract_text(image_path, lang='eng'):
    img = Image.open(image_path)
    img = preprocess_image(img)
    config = '--oem 3 --psm 6'
    return pytesseract.image_to_string(img, lang=lang, config=config)


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(1)
    image_path = sys.argv[1]
    if not pathlib.Path(image_path).is_file():
        sys.exit(1)
    text = extract_text(image_path, lang='eng')
    output_file = os.path.splitext(image_path)[0] + '.txt'
    with pathlib.Path(output_file).open('w', encoding='utf-8') as f:
        f.write(text)


if __name__ == '__main__':
    main()
