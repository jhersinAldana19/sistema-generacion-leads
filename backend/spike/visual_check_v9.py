"""Verifica: sin naranja, contenido de lista visible al hacer clic.
No es parte de la app."""

from playwright.sync_api import sync_playwright

FRONTEND = "http://localhost:5173"
OUT = "screenshots_v9"

import os
os.makedirs(OUT, exist_ok=True)


def main() -> None:
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})

        page.goto(FRONTEND)
        page.wait_for_timeout(1000)
        page.fill("#email", "sistemas@tecportla.com")
        page.fill("#password", "Tecport19$123jA!2026")
        page.click("button[type=submit]")
        page.wait_for_url(f"{FRONTEND}/", timeout=10000)
        page.wait_for_timeout(800)
        page.screenshot(path=f"{OUT}/01_no_orange.png")

        page.click("text=Listas guardadas")
        page.wait_for_timeout(400)
        page.click("text=Prospectos VIP")
        page.wait_for_timeout(1000)
        page.screenshot(path=f"{OUT}/02_list_contents.png")

        browser.close()


if __name__ == "__main__":
    main()
