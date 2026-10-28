Propunere dataset: Manuale școlare românești multimodale

1. De ce acest dataset? La ce e bun și cine l-ar folosi?

Scopul proiectului este construirea unui dataset multimodal din manuale școlare românești, prin extragerea și structurarea conținutului acestora: text, imagini, tabele și ecuații.

Problema pe care dorim să o rezolvăm este că simpla extragere a textului prin OCR clasic nu păstrează structura documentului și relațiile dintre elemente. De exemplu, o diagramă este adesea separată de paragraful care o explică, iar un tabel își pierde formatul logic. Datasetul nostru rezolvă acest neajuns prin organizarea conținutului ierarhic, la nivel de manual, pagină și element.

Principalele utilizări (cine l-ar folosi și la ce e bun):

Asistenți educaționali personalizați (AI Tutors): Acesta este principalul avantaj pentru elevi. Având acces la date structurate (text asociat corect cu imagini), un model de limbaj (LLM) poate prelua o lecție dificilă și o poate rescrie într-un limbaj prietenos, „mai uman” și pe înțelesul unui elev de clasa a V-a, adaptând complexitatea la nevoile copilului.

Sisteme RAG educaționale: Capabile să răspundă la întrebări punctuale folosind informații sigure din manuale și să indice cu exactitate pagina sau imaginea sursă.

Generarea automată de materiale: Crearea de rezumate, exerciții, sau flashcard-uri bazate direct pe programa școlară.

Ce aduce în plus? Există deja dataseturi precum Romanian FinePDFs (pentru OCR general) sau EduMUSE (pentru manuale în engleză). Datasetul nostru își propune să ofere o reprezentare structurată a manualelor școlare românești, combinând metadatele educaționale cu informațiile textuale și vizuale și relațiile dintre acestea.. Astfel, orice altă aplicație educațională pentru limba română va putea folosi aceste date fără să reproceseze manualele de la zero.

2. Surse (De unde luați datele)

Sursa utilizată în prototip:

Manuale.edu.ro – manualul „Limba și literatura română”, clasa a V-a, varianta PDF.

Dimensiune: export PDF de aprox. 246 de pagini; prototipul procesează local un eșantion de 30 de pagini (pg. 12–41).

Licență: Până la clarificarea drepturilor de redistribuire a conținutului extras de pe platforma Ministerului, datele brute procesate rămân locale (utilizare în scop educațional/cercetare).

3. Date sensibile

Manualele școlare nu conțin, în general, date personale (PII) ale elevilor. Pot apărea însă informații despre autori, fotografii cu persoane reale sau nume în cadrul exercițiilor (ex. „Maria are 5 mere”).

Cum le gestionăm: Vom rula un pas de validare (manuală/automatizată) pentru a ne asigura că nu extragem date sensibile. Informațiile bibliografice și numele autorilor vor fi păstrate strict pentru atribuirea corectă a surselor.
Notă: PDF-urile originale (datele brute) nu vor fi încărcate pe GitHub. Vom publica doar fișierele structurate (JSON/text/extrase), cu respectarea drepturilor de autor.

4. Schema datasetului

Datasetul va fi organizat ierarhic: Manual → Pagină → Element.
Fiecare pagină va reprezenta o înregistrare de tip JSONL, conținând o listă ordonată de elemente (text, image, table, equation).

Schema simplificată (format JSON):

{
  "page_id": "string",
  "manual_id": "string",
  "pdf_page_number": 12,
  "ocr_engine": "tesseract",
  "ocr_language": "ron",
  "elements": [
    {
      "element_id": "string",
      "type": "text | image | table | equation",
      "content": "Conținutul extras (text, path imagine sau structură tabel)"
    }
  ]
}


Exemple din datele reale (extragere text prin Tesseract OCR):

Exemplul 1 – Pagina PDF 12:

{
  "page_id": "art_romana_5_2022_p12",
  "manual_id": "art_romana_5_2022",
  "pdf_page_number": 12,
  "elements": [{
    "element_id": "text_1",
    "type": "text",
    "content": "COMPETENŢE GENERALE ȘI SPECIFICE"
  }]
}


Exemplul 2 – Pagina PDF 14:

{
  "page_id": "art_romana_5_2022_p14",
  "manual_id": "art_romana_5_2022",
  "pdf_page_number": 14,
  "elements": [{
    "element_id": "text_1",
    "type": "text",
    "content": "GHID DE UTILIZARE A MANUALULUI DIGITAL"
  }]
}


5. Cum vom demonstra utilitatea? (Opțional)

Pentru a demonstra utilitatea datasetului, vom realiza un prototip de asistent educațional AI, folosind Python și Streamlit.

Elevii vor putea adresa întrebări despre conceptele studiate, iar sistemul va recupera automat informațiile relevante din manuale, inclusiv imaginile asociate. Pe baza acestora, asistentul va genera explicații adaptate nivelului educațional al elevului și va indica paginile sursă.

Astfel, vom demonstra cum organizarea structurată a conținutului poate facilita dezvoltarea unor instrumente educaționale interactive.