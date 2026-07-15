"""
Segunda ronda del spike de extraccion: prueba fuentes que SI suelen nombrar
personas reales (gobierno corporativo, reportes de sostenibilidad en PDF),
descubiertas dinamicamente en la ronda anterior (explore_investor_pages.py).
Mismas reglas anti-alucinacion que run_extract_spike.py.
"""

import io
import json
from pathlib import Path

import httpx
import trafilatura
from pypdf import PdfReader

from crawl import extract_emails, extract_tel_links, fetch
from run_extract_spike import llm_extract

HTML_TARGETS = [
    "https://www.cementospacasmayo.com.pe/sostenibilidad/gobernanza/gobierno-corporativo",
]

PDF_TARGETS = [
    "https://www.antamina.com/wp-content/uploads/2025/11/reporte-de-sostenibilidad-2024-esp.pdf",
]

MAX_PDF_PAGES = 15  # las primeras paginas suelen tener el mensaje del gerente general / directorio


def extract_pdf_text(pdf_bytes: bytes, max_pages: int) -> str:
    reader = PdfReader(io.BytesIO(pdf_bytes))
    chunks = []
    for i, page in enumerate(reader.pages[:max_pages]):
        chunks.append(page.extract_text() or "")
    return "\n".join(chunks)


def process_html(url: str, client: httpx.Client) -> dict:
    html, error = fetch(url, client)
    if error:
        return {"url": url, "type": "html", "accessible": False, "error": error}
    text = trafilatura.extract(html, url=url, include_comments=False, include_tables=True) or ""
    emails = extract_emails(text) or extract_emails(html)
    phones = extract_tel_links(html)
    people = []
    notes_es = "Texto insuficiente."
    if len(text) >= 200:
        extraction = llm_extract(text, url)
        people = [p.model_dump() for p in extraction.people]
        notes_es = extraction.notes_es
    return {
        "url": url, "type": "html", "accessible": True, "text_length": len(text),
        "emails_found": emails, "phones_found": phones,
        "people_found": people, "notes_es": notes_es,
    }


def process_pdf(url: str, client: httpx.Client) -> dict:
    try:
        response = client.get(url, timeout=60, follow_redirects=True)
        response.raise_for_status()
    except httpx.HTTPError as exc:
        return {"url": url, "type": "pdf", "accessible": False, "error": str(exc)}

    text = extract_pdf_text(response.content, MAX_PDF_PAGES)
    emails = extract_emails(text)
    people = []
    notes_es = "Texto insuficiente."
    if len(text) >= 200:
        extraction = llm_extract(text, url)
        people = [p.model_dump() for p in extraction.people]
        notes_es = extraction.notes_es
    return {
        "url": url, "type": "pdf", "accessible": True, "text_length": len(text),
        "pages_read": MAX_PDF_PAGES,
        "emails_found": emails, "people_found": people, "notes_es": notes_es,
    }


def main() -> None:
    results = []
    with httpx.Client() as client:
        for url in HTML_TARGETS:
            print(f"\n=== HTML: {url} ===")
            result = process_html(url, client)
            results.append(result)
            print(json.dumps(result, indent=2, ensure_ascii=False))

        for url in PDF_TARGETS:
            print(f"\n=== PDF: {url} ===")
            result = process_pdf(url, client)
            results.append(result)
            print(json.dumps(result, indent=2, ensure_ascii=False))

    out_path = Path(__file__).parent / "extract_results_v2.json"
    out_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nResultados guardados en {out_path}")


if __name__ == "__main__":
    main()
