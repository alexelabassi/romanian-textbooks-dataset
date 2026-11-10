from pathlib import Path

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    PdfPipelineOptions,
    TesseractCliOcrOptions,
    OcrMode,
)
from docling.document_converter import (
    DocumentConverter,
    PdfFormatOption,
)

ROOT = Path(__file__).resolve().parents[1]

PDF_PATH = ROOT / "data/raw/Manual Română clasa a V-a.pdf"
OUTPUT_DIR = ROOT / "data/processed/docling"
IMAGES_DIR = OUTPUT_DIR / "images"


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    options = PdfPipelineOptions()

    # OCR cu Tesseract, în limba română
    options.do_ocr = True
    options.ocr_options = TesseractCliOcrOptions(
        lang=["ron"],
        tesseract_cmd=r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        mode=OcrMode.FULL_PAGE,
    )

    options.do_table_structure = True
    options.generate_picture_images = True
    options.images_scale = 2.0

    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_options=options
            )
        }
    )

    # Procesăm paginile 17–21
    result = converter.convert(
        PDF_PATH,
        page_range=(17, 21)
    )

    doc = result.document

    for i, table in enumerate(doc.tables, start=1):
        page = table.prov[0].page_no

        print(f"\n=== Tabelul {i}, pagina {page} ===")
        print(table.export_to_dataframe(doc=doc).to_string(index=False, header=False))

    # Eliminăm antetele și subsolurile detectate
    headers_footers = [
        item for item in doc.texts
        if item.label in ("page_header", "page_footer")
    ]

    doc.delete_items(node_items=headers_footers)

    print(f"Eliminate {len(headers_footers)} antete/subsoluri")

    # Salvăm documentul curățat
    doc.save_as_json(OUTPUT_DIR / "docling_raw.json")
    doc.save_as_markdown(OUTPUT_DIR / "preview.md")

    # Salvăm imaginile detectate
    for i, picture in enumerate(doc.pictures, start=1):
        image = picture.get_image(doc)

        if image is not None:
            image.save(IMAGES_DIR / f"image_{i}.png")

    print("Processed pages:", len(doc.pages))
    print("Text elements:", len(doc.texts))
    print("Detected pictures:", len(doc.pictures))
    print("Detected tables:", len(doc.tables))
    print("Output:", OUTPUT_DIR)


if __name__ == "__main__":
    main()