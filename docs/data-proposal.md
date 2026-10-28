# Propunere dataset: Manuale școlare românești multimodale

## 1. De ce acest dataset? La ce e bun și cine l-ar folosi?

Scopul proiectului este construirea unui dataset multimodal din manuale școlare românești, prin extragerea și structurarea textului, imaginilor, tabelelor și ecuațiilor.

Extragerea clasică prin OCR oferă textul unei pagini, dar nu păstrează întotdeauna structura documentului. De exemplu, o diagramă poate pierde legătura cu paragraful care o explică, iar un tabel poate fi transformat într-un șir de cuvinte fără organizarea pe rânduri și coloane. **Ne propunem** să păstrăm aceste relații printr-o structură ierarhică: manual → pagină → element.

Datasetul ar putea fi utilizat de dezvoltatori de aplicații educaționale, cercetători în NLP și profesori, în special pentru **asistenți educaționali AI**, **sisteme RAG** care răspund cu referințe la paginile sursă și **generarea de rezumate, exerciții și fișe de recapitulare**. Un asistent ar putea recupera explicația unui concept împreună cu imaginea relevantă și ar putea reformula lecția la nivelul unui elev de clasa a V-a.

Există dataseturi precum [Romanian FinePDFs](https://huggingface.co/datasets/OpenLLM-Ro/ro_sft_finepdfs), orientat către perechi imagine–text pentru OCR în română, și [EduMUSE](https://huggingface.co/datasets/upb-nlp/EduMUSE), cu exerciții multimodale din manuale în engleză. **Contribuția propusă** este o reprezentare specifică manualelor școlare românești, cu metadate educaționale, elemente de tipuri distincte și legături între conținutul textual și cel vizual. Astfel, aplicațiile ar putea reutiliza datele fără a reprocesa fiecare manual de la zero.

## 2. Surse

- **Sursa prototipului:** [Manuale.edu.ro – Limba și literatura română, clasa a V-a](https://manuale.edu.ro/manuale/Clasa%20a%20V-a/Limba%20si%20literatura%20romana/Qk9PSOxFVA/).
- **Dimensiune:** exportul PDF local are aproximativ **246 de pagini**; au fost procesate **30 de pagini (12–41)** cu Tesseract OCR, folosind limba `ron`.
- **Licență:** nu avem confirmate drepturi de redistribuire pentru textul și imaginile extrase din această sursă. Prin urmare, **PDF-ul și rezultatele OCR rămân locale** până la clarificarea drepturilor. Pentru un eșantion public vom folosi surse cu permisiuni de reutilizare adecvate.

## 3. Date sensibile

Manualele publice nu conțin, de regulă, date personale private ale elevilor, dar pot apărea nume, fotografii sau exemple cu informații identificabile. Vom verifica datele și vom elimina ori anonimiza informațiile personale nenecesare. Numele autorilor și metadatele bibliografice publice vor fi păstrate pentru atribuirea surselor.

**Datele brute (PDF-uri, scanări) nu vor fi încărcate pe GitHub.** Nici textul OCR și imaginile extrase nu vor fi publicate fără drepturi de reutilizare clarificate.

## 4. Schema datasetului

Structura este **Manual → Pagină → Element**. Metadatele manualului (titlu, clasă, materie, autori, sursă, licență) sunt păstrate separat. Fiecare linie din `pages.jsonl` reprezintă o pagină și conține o listă ordonată `elements`.

| Tip element | Câmpuri specifice |
|---|---|
| `text` | `text` |
| `image` | `image_path`, `caption`, `description`, `related_element_ids` |
| `table` | `rows`, `raw_text`, `image_path` |
| `equation` | `latex`, `raw_text`, `image_path` |

**Exemplul 1 — pagina PDF 12 (fragment real OCR, prescurtat):**

```json
{
  "page_id": "art_romana_5_2022_p12",
  "manual_id": "art_romana_5_2022",
  "pdf_page_number": 12,
  "ocr_engine": "tesseract",
  "ocr_language": "ron",
  "elements": [{
    "element_id": "art_romana_5_2022_p12_text_1",
    "type": "text",
    "text": "COMPETENŢE GENERALE ȘI SPECIFICE"
  }]
}
```

**Exemplul 2 — pagina PDF 14 (fragment real OCR, prescurtat):**

```json
{
  "page_id": "art_romana_5_2022_p14",
  "manual_id": "art_romana_5_2022",
  "pdf_page_number": 14,
  "ocr_engine": "tesseract",
  "ocr_language": "ron",
  "elements": [{
    "element_id": "art_romana_5_2022_p14_text_1",
    "type": "text",
    "text": "GHID DE UTILIZARE A MANUALULUI DIGITAL"
  }]
}
```

**Stadiu actual:** extragere OCR și export JSONL pentru elemente `text`. Schema Pydantic suportă și `image`, `table`, `equation`, urmând ca extragerea și asocierea acestora să fie implementate ulterior.

## 5. Cum vom demonstra utilitatea? (opțional)

Vom realiza un prototip de **asistent educațional AI** cu Python și Streamlit. Elevul va putea pune întrebări despre materia studiată, iar sistemul va recupera automat fragmentele relevante și, după extinderea multimodală, imaginile asociate. Asistentul va genera explicații adaptate nivelului școlar și va indica paginile sursă.

