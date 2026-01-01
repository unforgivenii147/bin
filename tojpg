#!/data/data/com.termux/files/usr/bin/env python3
import sys
import cv2
import numpy as np
from pathlib import Path

# Supported formats that OpenCV can generally decode
SUPPORTED_FORMATS = {'.png', '.bmp', '.tiff', '.webp', '.ico', '.jpg', '.jpeg'}


def convert_to_jpg(file_path: str) -> bool:
    """Convert an image to JPG using OpenCV, handling transparency with a white background."""
    path = Path(file_path)

    if not path.is_file() or path.suffix.lower() not in SUPPORTED_FORMATS:
        print(f'Skipping: {path.name} (Unsupported format or not a file)')
        return False

    # If already JPG, nothing to do
    if path.suffix.lower() in {'.jpg', '.jpeg'}:
        return True

    output_path = path.with_suffix('.jpg')

    # Ask before overwriting
    if output_path.exists():
        response = input(f"'{output_path.name}' exists. Overwrite? (y/n): "
                         ).strip().lower()
        if response != 'y':
            return False

    try:
        # Load image including alpha channel (-1 is IMREAD_UNCHANGED)
        img = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)

        if img is None:
            print(f'Error: Could not decode {path.name}')
            return False

        # Handle transparency (4 channels: BGR + Alpha)
        if img.shape[2] == 4:
            # Split channels
            b, g, r, a = cv2.split(img)
            # Create a white background
            white_bg = np.full(img.shape[:2], 255, dtype=np.uint8)

            # Normalize alpha to 0.0 - 1.0
            alpha = a.astype(float) / 255.0

            # Blend each channel with white background: (color * alpha) + (white * (1 - alpha))
            img_b = (b.astype(float) * alpha + white_bg.astype(float) *
                     (1 - alpha)).astype(np.uint8)
            img_g = (g.astype(float) * alpha + white_bg.astype(float) *
                     (1 - alpha)).astype(np.uint8)
            img_r = (r.astype(float) * alpha + white_bg.astype(float) *
                     (1 - alpha)).astype(np.uint8)

            final_img = cv2.merge((img_b, img_g, img_r))
        else:
            # If 3 channels, it's already BGR; if 1 channel, it's Grayscale
            final_img = img

        # Save as JPG (quality 95)
        success = cv2.imwrite(str(output_path), final_img,
                              [int(cv2.IMWRITE_JPEG_QUALITY), 95])

        if success:
            path.unlink()  # Delete original file
            print(f"Successfully converted '{path.name}' to jpg.")
            return True
        else:
            print(f"Failed to write '{output_path.name}'")
            return False

    except Exception as e:
        print(f"Error converting '{path.name}': {e}")
        return False


def main():
    if len(sys.argv) != 2:
        print(f'Usage: {sys.argv[0]} <image_file>')
        sys.exit(1)

    if convert_to_jpg(sys.argv[1]):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
