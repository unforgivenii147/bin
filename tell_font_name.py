#!/data/data/com.termux/files/usr/bin/python
import sys
from fontTools.ttLib import TTFont

def get_font_name(file_path):
    try:
        font = TTFont(file_path)
        for record in font['name'].names:
            if record.nameID == 1:  # Family name
                try:
                    # Try decoding with common encodings
                    return record.string.decode('utf-16-be').strip()
                except UnicodeDecodeError:
                    try:
                        return record.string.decode('utf-8').strip()
                    except UnicodeDecodeError:
                        try:
                            return record.string.decode('gb2312').strip()
                        except UnicodeDecodeError:
                            return record.string.decode('latin-1').strip()
    except Exception as e:
        return f"Error: {e}"

# Replace '02.ttf' with the path to your font file
font_name = get_font_name(sys.argv[1])
print("Font Name:", font_name)
