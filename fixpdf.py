#!/data/data/com.termux/files/usr/bin/env python3
import pdfminer.six
from pypdf import PdfReader, PdfWriter

reader = PdfReader("py.pdf", strict=False)
writer = PdfWriter()

for page in reader.pages:
    text = pdfminer.high_level.extract_text(page)
    print(text)
    writer.add_page(page)

with open("fixed.pdf", "wb") as f:
    writer.write(f)
