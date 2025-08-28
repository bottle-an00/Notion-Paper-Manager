import argparse
from pathlib import Path

from src.notion_paper_manager.config import settings
from src.notion_paper_manager.utils import ensure_dir
from src.notion_paper_manager.downloaders.arxiv_url2pdf import download_pdf_by_id
from src.notion_paper_manager.parsers.paper import fetch_arxiv_meta
from src.notion_paper_manager.clients.notion import NotionClient
from src.notion_paper_manager.extractors.figure import extract_figures_docling
from src.notion_paper_manager.extractors.extract_info_from_pdf import get_pdf_meta

def run(arxiv_id: str | None, pdf: str | None, add_to_notion: bool, extract_figures: bool,device: str):
    ensure_dir(settings.workdir_data)
    ensure_dir(settings.workdir_output)

    if arxiv_id:
        pdf_path = download_pdf_by_id(arxiv_id, settings.workdir_data)
        meta = fetch_arxiv_meta(arxiv_id)

    elif pdf:
        pdf_path = Path(pdf)
        meta = get_pdf_meta(pdf_path)

    else:
        raise SystemExit("Either --arxiv-id or --pdf must be provided.")

    print(f"[META] {meta['title']} ({meta['year']})")
    print(f"       Authors: {', '.join(meta['authors'])}")
    print(f"       PDF: {meta['pdf_url']}")

    figures = []
    if extract_figures:
        out = Path(f"{settings.workdir_output}/out_{meta['title']}")
        stats = extract_figures_docling(meta["pdf_url"], out, device=device)
        print(f"[DOC] figures: {stats['figures']}, tables: {stats['tables']}")

    if add_to_notion:
        nc = NotionClient()
        if pdf:
            page = nc.add_paper(settings.main.database_id, meta['title'], meta['authors'] or [], meta['year'] or 0,None,pdf_path,stats['figure_dir'], stats['table_dir'])
        else:
            page = nc.add_paper(settings.main.database_id, meta['title'], meta['authors'] or [], meta['year'] or 0,meta['pdf_url'],pdf_path,stats['figure_dir'], stats['table_dir'])
        print(f"[notion] page_id={page.get('id')}")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--arxiv-id", type=str)
    p.add_argument("--pdf", type=str)
    p.add_argument("--add-to-notion", default=True, action="store_true")
    p.add_argument("--extract-figures", default=True, action="store_true")
    p.add_argument("--device", type=str, default="cuda", choices=["cuda", "cpu"])
    args = p.parse_args()

    run(
        arxiv_id=getattr(args, "arxiv_id", None),
        pdf=getattr(args, "pdf", None),
        add_to_notion=getattr(args, "add_to_notion", False),
        extract_figures=getattr(args, "extract_figures", False),
        device=args.device
    )
