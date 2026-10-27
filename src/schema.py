
from typing import Annotated, Literal
from pydantic import BaseModel, Field
import pytesseract

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)& "C:\Program Files\Tesseract-OCR\tesseract.exe" --list-langs

class Manual(BaseModel):
    manual_id: str
    title: str
    subject: str
    grade: int = Field(ge=1, le=12)
    language: str = "ro"

    source_url: str
    license: str

    authors: list[str] = Field(default_factory=list)
    publisher: str | None = None
    year: int | None = None
    page_count: int = Field(gt=0)


class TextElement(BaseModel):
    element_id: str
    type: Literal["text"]
    text: str


class ImageElement(BaseModel):
    element_id: str
    type: Literal["image"]
    image_path: str

    caption: str | None = None
    description: str | None = None
    description_source: Literal["ai", "manual"] | None = None
    related_element_ids: list[str] = Field(default_factory=list)


class TableElement(BaseModel):
    element_id: str
    type: Literal["table"]

    rows: list[list[str]] | None = None
    raw_text: str | None = None
    image_path: str | None = None
    caption: str | None = None


class EquationElement(BaseModel):
    element_id: str
    type: Literal["equation"]

    raw_text: str | None = None
    latex: str | None = None
    image_path: str | None = None


Element = Annotated[
    TextElement | ImageElement | TableElement | EquationElement,
    Field(discriminator="type")
]


class Page(BaseModel):
    page_id: str
    manual_id: str
    pdf_page_number: int = Field(ge=1)

    ocr_engine: str
    ocr_language: str = "ron"

    elements: list[Element] = Field(default_factory=list)
