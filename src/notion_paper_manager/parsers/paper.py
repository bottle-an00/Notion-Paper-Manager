from dataclasses import dataclass
from pathlib import Path
import arxiv

@dataclass
class PaperMeta:
    title: str | None = None
    authors: list[str] | None = None
    year: int | None = None

def fetch_arxiv_meta(arxiv_id: str):
    paper = next(arxiv.Search(id_list=[arxiv_id]).results())
    title = paper.title
    authors = [a.name for a in paper.authors]
    year = paper.published.year
    pdf_url = paper.pdf_url
    return {"title": title, "authors": authors, "year": year, "pdf_url": pdf_url}
