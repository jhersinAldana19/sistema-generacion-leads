"""Verificacion visual de la pasada de diseno (contraste, ancho, logo).
No es parte de la app."""

from playwright.sync_api import sync_playwright

FRONTEND = "http://localhost:5173"
OUT = "screenshots_v4"

import os
os.makedirs(OUT, exist_ok=True)


def main() -> None:
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.on("pageerror", lambda exc: print(f"[pageerror] {exc}"))

        page.goto(FRONTEND)
        page.wait_for_timeout(1000)
        page.fill("#email", "sistemas@tecportla.com")
        page.fill("#password", "Tecport19$123jA!2026")
        page.click("button[type=submit]")
        page.wait_for_url(f"{FRONTEND}/", timeout=10000)
        page.wait_for_timeout(1000)

        page.click("text=Nueva conversación")
        page.wait_for_timeout(500)
        page.screenshot(path=f"{OUT}/01_sidebar_logo.png")

        composer = page.locator("textarea")
        composer.fill("Busca jefes de operaciones de empresas portuarias en Perú")
        composer.press("Enter")
        page.wait_for_selector("text=Entendí tu búsqueda", timeout=20000)
        page.wait_for_timeout(500)
        page.screenshot(path=f"{OUT}/02_criteria_card_wide.png")

        browser.close()


if __name__ == "__main__":
    main()
