import re
from pypdf import PdfReader
from pathlib import Path

def get_pdf_meta(pdf_path : Path):
    reader = PdfReader(pdf_path)
    info = reader.metadata
    title = info.title if info.title else None
    author = info.author if info.author else None
    creation_date = info.get('/CreationDate')
    year = 0
    if creation_date:
        match = re.search(r'D:(\d{4})', creation_date)
        if match:
            year = int(match.group(1))

    return {"title": title, "authors": [author] if author else [], "year": year, "pdf_url": pdf_path}
