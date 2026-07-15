"""
Spike de extraccion: valida si el pipeline (HTTPX + BeautifulSoup + Trafilatura +
regex + OpenAI) puede sacar de sitios REALES y PUBLICOS datos de contacto
verificables (correos, telefonos, personas con cargo), con fuente y evidencia,
sin inventar nada. No usa Playwright todavia (se evalua solo si hace falta).
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

import httpx
import trafilatura
from dotenv import load_dotenv
from openai import OpenAI

from crawl import discover_candidate_links, extract_emails, extract_phones, extract_tel_links, fetch
from extract_schema import PageExtraction

load_dotenv()

MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

SYSTEM_PROMPT = (
    "Extraes personas mencionadas con nombre y cargo en un texto proveniente de "
    "un sitio corporativo real. Reglas estrictas: "
    "1) Solo incluye personas cuyo nombre completo Y cargo aparezcan explicitamente "
    "escritos en el texto. "
    "2) No inventes ni infieras nombres, cargos, ni relaciones entre nombre y cargo "
    "que no esten escritas literalmente. "
    "3) Copia la evidencia textual exacta (verbatim) del fragmento del texto original. "
    "4) Si el texto no contiene ninguna persona con nombre y cargo, devuelve una "
    "lista vacia y explica brevemente por que en notes_es. "
    "5) No proceses el texto como si fuera de otra empresa: usa solo lo dado."
)

TARGETS = [
    {
        "name": "Minera Antamina",
        "homepage": "https://www.antamina.com",
        "sector": "minero",
    },
    {
        "name": "Cementos Pacasmayo",
        "homepage": "https://www.cementospacasmayo.com.pe",
        "sector": "cementero",
    },
    {
        "name": "APM Terminals Callao",
        "homepage": "https://www.apmterminals.com/en/callao",
        "sector": "portuario",
    },
]

MAX_PAGES_PER_COMPANY = 4


def llm_extract(text: str, url: str) -> PageExtraction:
    response = client.responses.parse(
        model=MODEL,
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"URL fuente: {url}\n\nTEXTO:\n{text[:8000]}"},
        ],
        text_format=PageExtraction,
    )
    return response.output_parsed


def process_page(url: str, client_http: httpx.Client) -> dict:
    retrieved_at = datetime.now(timezone.utc).isoformat()
    html, error = fetch(url, client_http)
    if error:
        return {"url": url, "accessible": False, "error": error, "retrieved_at": retrieved_at}

    clean_text = trafilatura.extract(html, url=url, include_comments=False, include_tables=False) or ""
    emails = extract_emails(clean_text) or extract_emails(html)
    phones = sorted(set(extract_tel_links(html)) | set(extract_phones(clean_text)))

    people: list[dict] = []
    notes_es = "Texto insuficiente para analizar (menos de 200 caracteres)."
    if len(clean_text) >= 200:
        extraction = llm_extract(clean_text, url)
        people = [p.model_dump() for p in extraction.people]
        notes_es = extraction.notes_es

    return {
        "url": url,
        "accessible": True,
        "retrieved_at": retrieved_at,
        "text_length": len(clean_text),
        "emails_found": emails,
        "phones_found": phones,
        "people_found": people,
        "notes_es": notes_es,
    }


def main() -> None:
    results = []
    with httpx.Client() as http_client:
        for target in TARGETS:
            print(f"\n=== {target['name']} ({target['sector']}) ===")
            homepage_html, home_error = fetch(target["homepage"], http_client)

            company_result = {
                "name": target["name"],
                "sector": target["sector"],
                "homepage": target["homepage"],
                "pages": [],
            }

            if home_error:
                print(f"  Homepage NO accesible: {home_error}")
                company_result["homepage_error"] = home_error
                results.append(company_result)
                continue

            candidates = discover_candidate_links(target["homepage"], homepage_html, limit=MAX_PAGES_PER_COMPANY - 1)
            pages_to_visit = [target["homepage"]] + candidates
            print(f"  Homepage OK. Paginas candidatas encontradas: {len(candidates)}")
            for link in candidates:
                print(f"    - {link}")

            for page_url in pages_to_visit:
                page_result = process_page(page_url, http_client)
                company_result["pages"].append(page_result)
                if page_result["accessible"]:
                    print(
                        f"  [{page_url}] texto={page_result['text_length']} chars, "
                        f"emails={page_result['emails_found']}, "
                        f"phones={page_result['phones_found']}, "
                        f"personas={len(page_result['people_found'])}"
                    )
                    for person in page_result["people_found"]:
                        print(f"      -> {person['full_name']} | {person['job_title']}")
                        print(f"         evidencia: {person['evidence_text'][:150]}")
                else:
                    print(f"  [{page_url}] NO accesible: {page_result['error']}")

            results.append(company_result)

    out_path = Path(__file__).parent / "extract_results.json"
    out_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nResultados guardados en {out_path}")


if __name__ == "__main__":
    main()
