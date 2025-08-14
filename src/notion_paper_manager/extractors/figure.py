# src/notion_paper_manager/extractors/figures_docling.py
from __future__ import annotations
from pathlib import Path

from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, AcceleratorOptions
from docling_core.types.doc import PictureItem, TableItem

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
