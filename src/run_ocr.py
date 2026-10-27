
from pathlib import Path
from io import BytesIO
import json

import pymupdf
import pytesseract
from PIL import Image


# Configuration
ROOT = Path(__file__).resolve().parents[1]

PDF_PATH = ROOT / "data/raw/Manual Română clasa a V-a.pdf"
OUTPUT_PATH = ROOT / "data/processed/pages.jsonl"

TESSERACT_PATH = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

MANUAL_ID = "art_romana_5_2022"
PAGES = list(range(12, 42))


def extract_text(page):
    # Render the PDF page as an image
    pix = page.get_pixmap(dpi=200, alpha=False)
    image = Image.open(
        BytesIO(pix.tobytes("png"))
    ).convert("RGB")

    # Apply OCR
    return pytesseract.image_to_string(
        image,
        lang="ron"
    ).strip()


def main():
    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with pymupdf.open(PDF_PATH) as pdf:
        with OUTPUT_PATH.open(
            "w", encoding="utf-8"
        ) as output:

            for page_number in PAGES:
                page = pdf[page_number - 1]
                text = extract_text(page)

                page_id = f"{MANUAL_ID}_p{page_number}"

                record = {
                    "page_id": page_id,
                    "manual_id": MANUAL_ID,
                    "pdf_page_number": page_number,
                    "ocr_engine": "tesseract",
                    "ocr_language": "ron",
                    "elements": [
                        {
                            "element_id": f"{page_id}_text_1",
                            "type": "text",
                            "text": text
                        }
                    ]
                }

                output.write(
                    json.dumps(
                        record,
                        ensure_ascii=False
                    ) + "\n"
                )

                print(
                    f"Page {page_number}: "
                    f"{len(text)} characters"
                )

    print("OCR completed successfully!")


if __name__ == "__main__":
    main()
