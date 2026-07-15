"""Descubrimiento de enlaces y extracción determinista (regex/DOM) sobre HTML.

Portado de backend/spike/crawl.py, ya validado contra sitios reales:
- Los teléfonos SOLO se toman de `tel:` o del texto ya limpio -- nunca de un
  regex libre sobre HTML crudo (produce falsos positivos: IDs, CSS, assets).
- extract_headings_and_paragraphs es el respaldo para layouts de "tarjetas"
  (nombre en <h*>, cargo en <p>) que Trafilatura descarta como boilerplate.
"""

import re
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36 "
    "TecportLeadIntelligence/0.1 (+investigacion comercial B2B, uso interno)"
)

CANDIDATE_KEYWORDS = [
    "equipo", "nosotros", "quienes-somos", "quienes_somos", "acerca",
    "directorio", "organigrama", "liderazgo", "gerencia", "contacto",
    "contact", "about", "team", "leadership", "management", "our-team",
]

INVESTOR_KEYWORDS = [
    "inversionista", "investor", "memoria-anual", "memoria_anual", "annual-report",
    "gobierno-corporativo", "reportes", "sostenibilidad", "plana-gerencial",
    "junta-directiva",
]

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
PHONE_RE = re.compile(
    r"(?:\+\d{1,3}[\s.-]?)?(?:\(\d{1,4}\)[\s.-]?)?\d{2,4}[\s.-]?\d{3,4}[\s.-]?\d{3,4}"
)


def fetch(url: str, client: httpx.Client) -> tuple[str | None, str | None]:
    """Devuelve (html, error). error es None si la descarga fue exitosa."""
    try:
        response = client.get(url, headers={"User-Agent": USER_AGENT}, follow_redirects=True, timeout=20)
        if response.status_code >= 400:
            return None, f"HTTP {response.status_code}"
        content_type = response.headers.get("content-type", "")
        if "text/html" not in content_type and "html" not in content_type:
            return None, f"content-type no html ({content_type})"
        return response.text, None
    except httpx.HTTPError as exc:
        return None, f"{type(exc).__name__}: {exc}"


def is_url_reachable(url: str, client: httpx.Client) -> bool:
    """Verificación obligatoria antes de confiar en cualquier URL 'descubierta'
    por el paso de discovery (ver services/search/discovery.py): en el spike,
    1 de 4 URLs devueltas por la IA no resolvía por DNS."""
    html, error = fetch(url, client)
    return error is None


def discover_candidate_links(base_url: str, html: str, keywords: list[str] = CANDIDATE_KEYWORDS, limit: int = 4) -> list[str]:
    soup = BeautifulSoup(html, "lxml")
    base_domain = urlparse(base_url).netloc
    seen: set[str] = set()
    candidates: list[str] = []
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        text = a.get_text(strip=True).lower()
        haystack = f"{href.lower()} {text}"
        if not any(keyword in haystack for keyword in keywords):
            continue
        absolute = urljoin(base_url, href)
        parsed = urlparse(absolute)
        if parsed.netloc != base_domain:
            continue
        if parsed.scheme not in ("http", "https"):
            continue
        clean = absolute.split("#")[0]
        if clean in seen or clean == base_url.rstrip("/"):
            continue
        seen.add(clean)
        candidates.append(clean)
        if len(candidates) >= limit:
            break
    return candidates


def extract_emails(text: str) -> list[str]:
    return sorted(set(EMAIL_RE.findall(text)))


def extract_headings_and_paragraphs(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "noscript", "svg"]):
        tag.decompose()
    lines = []
    for el in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p", "li"]):
        text = el.get_text(strip=True)
        if text:
            lines.append(text)
    return "\n".join(lines)


def extract_tel_links(html: str) -> list[str]:
    soup = BeautifulSoup(html, "lxml")
    found = []
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if href.lower().startswith("tel:"):
            number = href[4:].strip()
            if number:
                found.append(number)
    return sorted(set(found))


def extract_phones_from_clean_text(text: str) -> list[str]:
    found = []
    for match in PHONE_RE.finditer(text):
        candidate = match.group().strip()
        digits = re.sub(r"\D", "", candidate)
        if len(digits) >= 7:
            found.append(candidate)
    return sorted(set(found))
