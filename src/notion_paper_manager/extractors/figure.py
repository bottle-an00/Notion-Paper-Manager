# src/notion_paper_manager/extractors/figures_docling.py
from __future__ import annotations
from pathlib import Path

from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, AcceleratorOptions
from docling_core.types.doc import PictureItem, TableItem

def _passes_filters(img, *,
                    min_width=100,       # 최소 가로(px)
                    min_height=100,      # 최소 세로(px)
                    min_area=60_000,     # 최소 면적(px^2)
                    min_ar=0.2,          # 최소 가로세로비 (w/h)
                    max_ar=10.0):         # 최대 가로세로비 (w/h)
    w, h = img.size
    if w < min_width or h < min_height:
        return False
    if w * h < min_area:
        return False
    ar = w / h if h else 0
    if not (min_ar <= ar <= max_ar):
        return False
    return True

def run_docling_pipeline(pdf_source: str, outdir: Path, device: str) -> list[Path]:

    outdir.mkdir(parents=True, exist_ok=True)

    pipe = PdfPipelineOptions()
    if(device == "cpu"):
        accelerator_options = AcceleratorOptions()
        accelerator_options.device = "cpu"
        pipe = PdfPipelineOptions(accelerator_options=accelerator_options)

    pipe.images_scale = 2.0
    pipe.generate_page_images = True
    pipe.generate_picture_images = True

    converter = DocumentConverter(
        format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipe)}
    )
    conv = converter.convert(pdf_source)

    pic_idx, tbl_idx = 0, 0
    for elem, _level in conv.document.iterate_items():
        if isinstance(elem, PictureItem):
            img = elem.get_image(conv.document)
            if _passes_filters(img):
                pic_idx += 1
                figure_dir = outdir / Path("figures")
                figure_dir.mkdir(parents=True, exist_ok=True)
                with (figure_dir / f"figure-{pic_idx}.png").open("wb") as fp:
                    elem.get_image(conv.document).save(fp, "PNG")

        table_dir = outdir / Path("tables")
        table_dir.mkdir(parents=True, exist_ok=True)
        if isinstance(elem, TableItem):
            tbl_idx += 1
            with (table_dir / f"table-{tbl_idx}.png").open("wb") as fp:
                elem.get_image(conv.document).save(fp, "PNG")

    for i, table in enumerate(conv.document.tables, start=1):
        df = table.export_to_dataframe()
        df.to_csv(table_dir / f"table-{i}.csv", index=False)
        (table_dir / f"table-{i}.html").write_text(table.export_to_html(doc=conv.document), encoding="utf-8")


    return {"figures": pic_idx, "tables": len(conv.document.tables), "figure_dir": figure_dir, "table_dir": table_dir}

def extract_figures_docling(pdf_source: str, outdir: str | Path, device:str) -> list[Path]:
    outdir = Path(outdir)
    return run_docling_pipeline(pdf_source, outdir,device)
