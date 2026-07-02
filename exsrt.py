#!/data/data/com.termux/files/usr/bin/python
"""
A utility to extract subtitle tracks from video files using ffmpeg.
"""

import subprocess
import sys
import os
import shutil


def check_ffmpeg():
    """
    Checks if ffmpeg is installed and available in the system PATH.
    
    Returns:
        bool: True if ffmpeg is found, False otherwise.
    """
    return shutil.which("ffmpeg") is not None


def extract_subtitles(input_file, output_dir="subtitles"):
    """
    Extracts the first subtitle track from a video file and saves it as an .srt file.
    
    Args:
        input_file (str): Path to the input video file.
        output_dir (str): Directory where the subtitle file will be saved.
    """
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        return

    if not check_ffmpeg():
        print("Error: 'ffmpeg' is not installed or not in PATH.")
        return

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_file = os.path.join(output_dir, "subtitles.srt")
    
    # -y overwrites output if it exists
    # -map 0:s:0 selects the first subtitle stream
    command = [
        "ffmpeg",
        "-y",
        "-i", input_file,
        "-map", "0:s:0?",
        output_file
    ]

    print(f"Executing: {' '.join(command)}")
    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode == 0:
        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            print(f"Subtitles extracted and saved to {output_file}")
        else:
            print("No subtitle streams found or extraction resulted in an empty file.")
    else:
        print(f"Error during extraction: {result.stderr}")


def main():
    """
    Main entry point for the script. Parses command line arguments.
    """
    if len(sys.argv) != 2:
        print(f"Usage: python {os.path.basename(__name__)}.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    extract_subtitles(input_file)


if __name__ == "__main__":
    main()
