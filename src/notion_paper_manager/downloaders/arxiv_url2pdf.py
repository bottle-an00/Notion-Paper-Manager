import re
import arxiv
from pathlib import Path

ARXIV_NEW = re.compile(r'(\d{4}\.\d{4,5}(?:v\d+)?)')
ARXIV_OLD = re.compile(r'([a-z\-]+/\d{7}(?:v\d+)?)', re.I)

def to_arxiv_id(text: str) -> str:
    t = text.strip()
    t = t.split("arxiv:", 1)[-1] if t.lower().startswith("arxiv:") else t
    for pat in (ARXIV_NEW, ARXIV_OLD):
        m = pat.search(t)
        if m:
            return m.group(1)

    t = re.sub(r'.*/abs/', '', t)
    t = re.sub(r'.*/pdf/', '', t)
    t = re.sub(r'\.pdf$', '', t)
    if ARXIV_NEW.fullmatch(t) or ARXIV_OLD.fullmatch(t):
        return t
    raise ValueError(f"arXiv ID를 인식하지 못함: {text}")


def download_pdf_by_id(arxiv_id: str, outdir: str | Path) -> Path:
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    search = arxiv.Search(id_list=[arxiv_id])
    paper = next(search.results())
    pdf_path = outdir / f"{paper.get_short_id()}.pdf"
    paper.download_pdf(filename=str(pdf_path))
    return pdf_path
