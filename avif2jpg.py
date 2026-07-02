#!/usr/bin/env python3
"""Converts AVIF images to JPEG format.

This script scans a specified input directory for AVIF images and converts
them to JPEG format, saving the results in an output directory.
"""

import os
from pathlib import Path

import pillow_avif  # noqa: F401
from PIL import Image


def convert_avif_to_jpg(input_dir: str, output_dir: str) -> None:
    """Converts all AVIF files in input_dir to JPG in output_dir.

    Args:
        input_dir: Path to the directory containing AVIF files.
        output_dir: Path to the directory where JPG files will be saved.
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)

    output_path.mkdir(exist_ok=True, parents=True)

    if not input_path.exists():
        print(f"Error: Input directory '{input_dir}' does not exist.")
        return

    converted_count = 0
    for file in input_path.glob("*"):
        if file.suffix.lower() in {".avif", ".aviff"}:
            target_file = output_path / f"{file.stem}.jpg"
            
            try:
                with Image.open(file) as img:
                    # Convert to RGB to ensure JPEG compatibility
                    rgb_img = img.convert("RGB")
                    rgb_img.save(target_file, "JPEG", quality=95)
                print(f"Converted: {file.name} -> {target_file.name}")
                converted_count += 1
            except Exception as e:
                print(f"Error converting {file.name}: {e}")

    print(f"Total images converted: {converted_count}")


def main() -> None:
    """Main execution function for AVIF to JPG conversion."""
    # Use defaults or allow customization
    input_directory = "avif_images"
    output_directory = "jpg_images"
    
    convert_avif_to_jpg(input_directory, output_directory)


if __name__ == "__main__":
    main()
