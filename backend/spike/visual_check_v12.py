"""Verifica: estrella de favorito, seccion 'Busquedas favoritas' solo con
marcadas, eliminar lista y desmarcar favorito desde el sidebar.
No es parte de la app."""

from playwright.sync_api import sync_playwright

FRONTEND = "http://localhost:5173"
OUT = "screenshots_v12"

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
        page.wait_for_timeout(800)

        # abrir la primera conversacion del historial (que tiene una busqueda)
        page.locator("aside p:text('HISTORIAL') ~ ul button").first.click()
        page.wait_for_timeout(1000)
        page.screenshot(path=f"{OUT}/01_before_favorite.png")

        star = page.locator('button[aria-label="Marcar como favorita"]').first
        if star.count() > 0:
            star.click()
            page.wait_for_timeout(600)
            page.screenshot(path=f"{OUT}/02_after_favorite.png")

        page.click("text=Búsquedas favoritas")
        page.wait_for_timeout(800)
        page.screenshot(path=f"{OUT}/03_favorites_section.png")

        browser.close()


if __name__ == "__main__":
    main()
