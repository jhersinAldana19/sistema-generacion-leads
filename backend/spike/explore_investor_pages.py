"""
Exploracion (no productiva): descubre, a partir del propio homepage, si hay
secciones de 'relacion con inversionistas' / 'memoria anual' / 'gobierno
corporativo', que suelen listar nombres reales de la plana gerencial. No
inventa ninguna URL: solo sigue enlaces que existan literalmente en la pagina.
"""

from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

from crawl import USER_AGENT, fetch

INVESTOR_KEYWORDS = [
    "inversionista", "investor", "memoria-anual", "memoria_anual", "annual-report",
    "gobierno-corporativo", "reportes", "sostenibilidad", "plana-gerencial",
    "directorio", "junta-directiva",
]

HOMEPAGES = [
    "https://www.antamina.com",
    "https://www.cementospacasmayo.com.pe",
]


def find_links(base_url: str, html: str, keywords: list[str], limit: int = 8) -> list[str]:
    soup = BeautifulSoup(html, "lxml")
    base_domain = urlparse(base_url).netloc
    seen: set[str] = set()
    found: list[str] = []
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        text = a.get_text(strip=True).lower()
        haystack = f"{href.lower()} {text}"
        if not any(k in haystack for k in keywords):
            continue
        absolute = urljoin(base_url, href).split("#")[0]
        parsed = urlparse(absolute)
        if parsed.netloc != base_domain:
            continue
        if absolute in seen:
            continue
        seen.add(absolute)
        found.append(absolute)
        if len(found) >= limit:
            break
    return found


def main() -> None:
    with httpx.Client() as client:
        for homepage in HOMEPAGES:
            print(f"\n=== {homepage} ===")
            html, error = fetch(homepage, client)
            if error:
                print(f"  homepage no accesible: {error}")
                continue

            investor_links = find_links(homepage, html, INVESTOR_KEYWORDS)
            if not investor_links:
                print("  No se encontraron enlaces de inversionistas/gobierno corporativo en el homepage.")
                continue

            for link in investor_links:
                print(f"  candidato: {link}")

            # seguimos un nivel mas en el primer candidato para ver si hay PDFs o listados de personas
            first = investor_links[0]
            sub_html, sub_error = fetch(first, client)
            if sub_error:
                print(f"    -> no accesible: {sub_error}")
                continue
            pdf_links = [
                urljoin(first, a["href"]) for a in BeautifulSoup(sub_html, "lxml").find_all("a", href=True)
                if a["href"].lower().strip().endswith(".pdf")
            ]
            deeper_links = find_links(first, sub_html, INVESTOR_KEYWORDS + ["memoria", "reporte", "informe"], limit=8)
            print(f"    -> PDFs encontrados en esa pagina: {len(pdf_links)}")
            for p in pdf_links[:5]:
                print(f"       PDF: {p}")
            print(f"    -> Enlaces relacionados adicionales: {len(deeper_links)}")
            for d in deeper_links[:5]:
                print(f"       link: {d}")


if __name__ == "__main__":
    main()
