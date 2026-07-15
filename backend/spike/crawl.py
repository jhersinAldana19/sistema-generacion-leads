import re
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36 "
    "TecportLeadIntelligence-Spike/0.1 (+investigacion interna, uso no comercial)"
)

CANDIDATE_KEYWORDS = [
    "equipo", "nosotros", "quienes-somos", "quienes_somos", "acerca",
    "directorio", "organigrama", "liderazgo", "gerencia", "contacto",
    "contact", "about", "team", "leadership", "management", "our-team",
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


def discover_candidate_links(base_url: str, html: str, limit: int = 3) -> list[str]:
    soup = BeautifulSoup(html, "lxml")
    base_domain = urlparse(base_url).netloc
    seen: set[str] = set()
    candidates: list[str] = []
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        text = a.get_text(strip=True).lower()
        haystack = f"{href.lower()} {text}"
        if not any(keyword in haystack for keyword in CANDIDATE_KEYWORDS):
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
    """Texto de respaldo cuando la pagina usa un layout de 'tarjetas' (nombre en
    <h*>, cargo en <p>) que Trafilatura puede descartar como boilerplate.
    Menos limpio que Trafilatura (puede incluir nav/menus), pero no pierde
    nombres reales que si estan en el HTML."""
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
    """Telefonos declarados explicitamente en atributos href='tel:...'. Es la
    unica fuente de telefono confiable a partir de HTML crudo: buscar numeros
    sueltos en todo el HTML produce demasiados falsos positivos (IDs, CSS,
    assets, analytics)."""
    soup = BeautifulSoup(html, "lxml")
    found = []
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if href.lower().startswith("tel:"):
            number = href[4:].strip()
            if number:
                found.append(number)
    return sorted(set(found))


def extract_phones(text: str) -> list[str]:
    found = []
    for match in PHONE_RE.finditer(text):
        candidate = match.group().strip()
        digits = re.sub(r"\D", "", candidate)
        if len(digits) >= 7:
            found.append(candidate)
    return sorted(set(found))
