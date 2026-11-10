
import json
from collections import Counter
from pathlib import Path

from pydantic import BaseModel, ValidationError
from src import schema

ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = ROOT / "data/processed/docling/pages.jsonl"

ALLOWED_TYPES = {"text", "image", "table", "equation"}


def get_page_model():
    """Identifică modelul Pydantic pentru o pagină."""

    models = []

    for obj in vars(schema).values():
        if (
            isinstance(obj, type)
            and issubclass(obj, BaseModel)
            and obj.__module__ == schema.__name__
            and {"page_id", "elements"}.issubset(obj.model_fields)
        ):
            models.append(obj)

    if len(models) != 1:
        raise RuntimeError(
            "Nu am găsit un model unic pentru pagină "
            "în src/schema.py."
        )

    return models[0]


def check_image(image_path, page, element_id, errors):
    """Verifică dacă imaginea există pe disc."""

    if not isinstance(image_path, str) or not image_path.strip():
        errors.append(
            f"{page}/{element_id}: image_path lipsește"
        )
        return

    relative = Path(image_path.replace("\\", "/"))

    if relative.is_absolute() or ".." in relative.parts:
        errors.append(
            f"{page}/{element_id}: cale imagine invalidă"
        )
        return

    full_path = DATASET_PATH.parent / relative

    if not full_path.is_file():
        errors.append(
            f"{page}/{element_id}: imagine inexistentă: {full_path}"
        )
    elif full_path.stat().st_size == 0:
        errors.append(
            f"{page}/{element_id}: imagine goală"
        )


def validate_dataset():
    if not DATASET_PATH.exists():
        print(f"Datasetul nu există: {DATASET_PATH}")
        return

    PageModel = get_page_model()

    errors = []
    warnings = []

    page_ids = set()
    element_ids = set()

    counts = Counter()

    with DATASET_PATH.open(encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):

            if not line.strip():
                continue

            # 1. Verificăm că linia este JSON valid
            try:
                page = json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append(
                    f"Linia {line_number}: JSON invalid: {exc}"
                )
                continue

            if not isinstance(page, dict):
                errors.append(
                    f"Linia {line_number}: pagina nu este obiect JSON"
                )
                continue

            # 2. Validăm structura folosind Pydantic
            try:
                PageModel.model_validate(page)
            except ValidationError as exc:
                for error in exc.errors():
                    field = ".".join(map(str, error["loc"]))
                    errors.append(
                        f"Linia {line_number}, {field}: {error['msg']}"
                    )

            counts["pages"] += 1

            page_id = page.get("page_id")
            elements = page.get("elements")

            # 3. Verificăm ID-ul paginii
            if not isinstance(page_id, str) or not page_id.strip():
                errors.append(
                    f"Linia {line_number}: page_id invalid"
                )
                page_id = f"line_{line_number}"

            if page_id in page_ids:
                errors.append(
                    f"Page ID duplicat: {page_id}"
                )

            page_ids.add(page_id)

            if not isinstance(elements, list):
                errors.append(
                    f"{page_id}: elements nu este o listă"
                )
                continue

            current_elements = {}
            image_links = []

            # 4. Verificăm fiecare element
            for position, element in enumerate(elements, start=1):

                if not isinstance(element, dict):
                    errors.append(
                        f"{page_id}: elementul {position} este invalid"
                    )
                    continue

                element_id = element.get("element_id")
                element_type = element.get("type")

                if not isinstance(element_id, str) or not element_id:
                    errors.append(
                        f"{page_id}: element_id invalid"
                    )
                    continue

                if element_id in element_ids:
                    errors.append(
                        f"Element ID duplicat: {element_id}"
                    )

                element_ids.add(element_id)

                if element_type not in ALLOWED_TYPES:
                    errors.append(
                        f"{element_id}: tip invalid: {element_type}"
                    )
                    continue

                counts[element_type] += 1
                current_elements[element_id] = element_type

                # TEXT
                if element_type == "text":

                    text = element.get("text")

                    if not isinstance(text, str) or not text.strip():
                        errors.append(
                            f"{element_id}: text gol sau invalid"
                        )

                    label = element.get("label")

                    if label is not None and not isinstance(label, str):
                        errors.append(
                            f"{element_id}: label invalid"
                        )

                # IMAGE
                elif element_type == "image":

                    check_image(
                        element.get("image_path"),
                        page_id,
                        element_id,
                        errors
                    )

                    links = element.get("related_element_ids", [])

                    if not isinstance(links, list):
                        errors.append(
                            f"{element_id}: related_element_ids invalid"
                        )
                    elif not all(isinstance(x, str) for x in links):
                        errors.append(
                            f"{element_id}: referințele trebuie să fie stringuri"
                        )
                    else:
                        image_links.append((element_id, links))

                # TABLE
                elif element_type == "table":

                    rows = element.get("rows")

                    if rows is not None:
                        valid_rows = (
                            isinstance(rows, list)
                            and all(
                                isinstance(row, list)
                                and all(isinstance(cell, str) for cell in row)
                                for row in rows
                            )
                        )

                        if not valid_rows:
                            errors.append(
                                f"{element_id}: rows invalid"
                            )

                    if rows == [] and not element.get("raw_text"):
                        warnings.append(
                            f"{element_id}: tabel fără conținut"
                        )

                    if element.get("image_path"):
                        check_image(
                            element["image_path"],
                            page_id,
                            element_id,
                            errors
                        )

                # EQUATION
                elif element_type == "equation":

                    if not any(
                        element.get(key)
                        for key in ("latex", "raw_text", "image_path")
                    ):
                        warnings.append(
                            f"{element_id}: ecuație fără conținut"
                        )

                    if element.get("image_path"):
                        check_image(
                            element["image_path"],
                            page_id,
                            element_id,
                            errors
                        )

            # 5. Verificăm relațiile imagine-text
            for image_id, links in image_links:
                for referenced_id in links:

                    if referenced_id not in current_elements:
                        errors.append(
                            f"{image_id}: referință inexistentă: "
                            f"{referenced_id}"
                        )

                    elif current_elements[referenced_id] != "text":
                        errors.append(
                            f"{image_id}: referința {referenced_id} "
                            "nu indică un text"
                        )

    # 6. Afișăm rezultatele
    print("\n========== VALIDARE DATASET ==========")

    print(f"Schema: {PageModel.__name__}")
    print(f"Pagini: {counts['pages']}")
    print(f"Texte: {counts['text']}")
    print(f"Imagini: {counts['image']}")
    print(f"Tabele: {counts['table']}")
    print(f"Ecuații: {counts['equation']}")

    print(f"\nErori: {len(errors)}")
    print(f"Avertismente: {len(warnings)}")

    for error in errors[:25]:
        print(f"[ERROR] {error}")

    for warning in warnings[:25]:
        print(f"[WARNING] {warning}")

    if errors:
        print("\nREZULTAT: DATASET INVALID")
    elif counts["pages"] == 0:
        print("\nREZULTAT: DATASET GOL")
    else:
        print("\nREZULTAT: DATASET VALID STRUCTURAL")


if __name__ == "__main__":
    validate_dataset()
