import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = ROOT / "data/processed/docling/docling_raw.json"

PAGE_NUMBER = 17

with open(JSON_PATH, encoding="utf-8") as f:
    doc = json.load(f)

print(f"\n=== PAGE {PAGE_NUMBER} ===\n")

for item in doc["texts"]:
    if any(
        prov["page_no"] == PAGE_NUMBER
        for prov in item.get("prov", [])
    ):
        print(f"[{item['label']}] {item['text']}\n")

for key in ("pictures", "tables"):
    count = sum(
        any(p["page_no"] == PAGE_NUMBER for p in item.get("prov", []))
        for item in doc.get(key, [])
    )
    print(f"{key}: {count}")
