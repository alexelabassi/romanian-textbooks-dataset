
import base64
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

INPUT_PATH = ROOT / "data/processed/docling/docling_raw.json"
OUTPUT_DIR = ROOT / "data/processed/docling"
OUTPUT_PATH = OUTPUT_DIR / "pages.jsonl"
IMAGES_DIR = OUTPUT_DIR / "images"

MANUAL_ID = "art_romana_5_2022"


def main():
    with INPUT_PATH.open(encoding="utf-8") as f:
        doc = json.load(f)

    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    # Indexăm elementele folosind referințele Docling
    index = {}

    for section in ("texts", "pictures", "tables", "groups"):
        for item in doc.get(section, []):
            index[item["self_ref"]] = item

    # Creăm câte o înregistrare pentru fiecare pagină
    records = {}

    for page_str in doc["pages"]:
        page_no = int(page_str)

        records[page_no] = {
            "page_id": f"{MANUAL_ID}_p{page_no}",
            "manual_id": MANUAL_ID,
            "pdf_page_number": page_no,
            "ocr_engine": "tesseract",
            "ocr_language": "ron",
            "elements": []
        }

    counts = defaultdict(lambda: defaultdict(int))
    seen = set()

    def page_number(item):
        provenance = item.get("prov", [])
        return int(provenance[0]["page_no"]) if provenance else None

    def append_text(item, page_no):
        if item.get("label") in ("page_header", "page_footer"):
            return None

        text = item.get("text", "").strip()
        marker = item.get("marker", "").strip()

        # Păstrăm numerotarea exercițiilor și listelor
        if marker and not text.startswith(marker):
            text = f"{marker} {text}"

        if not text:
            return None

        counts[page_no]["text"] += 1
        ordinal = counts[page_no]["text"]

        element_id = f"{MANUAL_ID}_p{page_no}_text_{ordinal}"

        # Păstrăm clasificarea originală din Docling
        records[page_no]["elements"].append({
            "element_id": element_id,
            "type": "text",
            "label": item.get("label") or "text",
            "text": text
        })

        return element_id

    def append_picture(item, page_no):
        image = item.get("image") or {}
        uri = image.get("uri", "")

        if not uri.startswith("data:image/") or ";base64," not in uri:
            print(f"Warning: imagine lipsă pe pagina {page_no}")
            return None

        counts[page_no]["image"] += 1
        ordinal = counts[page_no]["image"]

        extension = (
            "jpg" if uri.startswith("data:image/jpeg") else "png"
        )

        filename = f"{MANUAL_ID}_p{page_no}_img{ordinal}.{extension}"
        destination = IMAGES_DIR / filename

        # Extragem imaginea Base64 din JSON-ul Docling
        destination.write_bytes(
            base64.b64decode(uri.split(",", 1)[1])
        )

        element = {
            "element_id": f"{MANUAL_ID}_p{page_no}_image_{ordinal}",
            "type": "image",
            "image_path": f"images/{filename}",
            "related_element_ids": []
        }

        records[page_no]["elements"].append(element)

        return element

    def append_table(item, page_no):
        grid = item.get("data", {}).get("grid", [])

        rows = [
            [cell.get("text", "") for cell in row]
            for row in grid
        ]

        counts[page_no]["table"] += 1
        ordinal = counts[page_no]["table"]

        records[page_no]["elements"].append({
            "element_id": f"{MANUAL_ID}_p{page_no}_table_{ordinal}",
            "type": "table",
            "rows": rows,
            "raw_text": "\n".join(
                "\t".join(row) for row in rows
            )
        })

    def visit(ref, parent_picture=None):
        if isinstance(ref, dict):
            ref = ref.get("$ref")

        if not ref or ref in seen or ref not in index:
            return

        seen.add(ref)
        item = index[ref]
        section = ref.split("/")[1]

        # Parcurgem recursiv grupurile
        if section == "groups":
            for child in item.get("children", []):
                visit(child, parent_picture=parent_picture)
            return

        page_no = page_number(item)

        if page_no not in records:
            return

        if section == "texts":
            text_id = append_text(item, page_no)

            # Asociem textul aflat în interiorul unei imagini
            if parent_picture is not None and text_id is not None:
                parent_picture["related_element_ids"].append(text_id)

        elif section == "pictures":
            picture_element = append_picture(item, page_no)

            for child in item.get("children", []):
                visit(child, parent_picture=picture_element)

        elif section == "tables":
            append_table(item, page_no)

    # Parcurgem documentul în ordinea Docling
    for child in doc["body"]["children"]:
        visit(child)

    # Exportăm datasetul în JSONL
    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        for page_no in sorted(records):
            record = records[page_no]

            f.write(
                json.dumps(record, ensure_ascii=False) + "\n"
            )

    print("Output:", OUTPUT_PATH)

    for page_no in sorted(records):
        summary = ", ".join(
            f"{key}={value}"
            for key, value in sorted(counts[page_no].items())
        )

        print(f"Page {page_no}: {summary or 'no elements'}")


if __name__ == "__main__":
    main()
