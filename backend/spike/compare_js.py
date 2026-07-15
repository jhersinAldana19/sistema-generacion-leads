"""
Compara el HTML estatico (httpx, sin JS) contra el HTML renderizado
(Playwright/Chromium, con JS) para las mismas paginas, para saber si el
contenido de personas/cargos esta oculto detras de JavaScript.
"""

import httpx
import trafilatura
from playwright.sync_api import sync_playwright

from crawl import USER_AGENT, fetch

URLS = [
    "https://www.apmterminals.com/en/callao/about/apm-terminals-callao",
]


def render_with_playwright(url: str, browser) -> str | None:
    page = browser.new_page(user_agent=USER_AGENT)
    try:
        page.goto(url, timeout=30000, wait_until="domcontentloaded")
        page.wait_for_timeout(4000)
        html = page.content()
        return html
    except Exception as exc:
        print(f"  Playwright error: {exc}")
        return None
    finally:
        page.close()


def main() -> None:
    with httpx.Client() as http_client, sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        for url in URLS:
            print(f"\n=== {url} ===")

            static_html, error = fetch(url, http_client)
            static_text = trafilatura.extract(static_html, url=url) if static_html else ""
            static_len = len(static_text or "")
            print(f"  httpx (estatico):     {static_len} chars de texto limpio" if not error else f"  httpx error: {error}")

            rendered_html = render_with_playwright(url, browser)
            rendered_text = trafilatura.extract(rendered_html, url=url) if rendered_html else ""
            rendered_len = len(rendered_text or "")
            print(f"  Playwright (con JS):  {rendered_len} chars de texto limpio")

            diff = rendered_len - static_len
            print(f"  Diferencia: {diff:+d} chars {'(JS revela contenido adicional)' if diff > 200 else '(sin diferencia relevante)'}")

        browser.close()


if __name__ == "__main__":
    main()
