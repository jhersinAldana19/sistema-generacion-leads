"""Verificacion de responsive + fondo con tinte + estado vacio de listas.
No es parte de la app."""

from playwright.sync_api import sync_playwright

FRONTEND = "http://localhost:5173"
OUT = "screenshots_v5"

import os
os.makedirs(OUT, exist_ok=True)


def login(page):
    page.goto(FRONTEND)
    page.wait_for_timeout(1000)
    page.fill("#email", "sistemas@tecportla.com")
    page.fill("#password", "Tecport19$123jA!2026")
    page.click("button[type=submit]")
    page.wait_for_url(f"{FRONTEND}/", timeout=10000)
    page.wait_for_timeout(800)


def main() -> None:
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)

        # Desktop
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        login(page)
        page.screenshot(path=f"{OUT}/01_desktop.png")
        page.close()

        # Mobile (iPhone-ish)
        page = browser.new_page(viewport={"width": 390, "height": 844})
        login(page)
        page.screenshot(path=f"{OUT}/02_mobile_sidebar_closed.png")

        page.click('button[aria-label="Abrir menú"]')
        page.wait_for_timeout(400)
        page.screenshot(path=f"{OUT}/03_mobile_sidebar_open.png")
        page.close()

        browser.close()


if __name__ == "__main__":
    main()
