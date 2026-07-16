"""Verificacion de la pasada de diseno con acento, avatares e iconos, y del
fix de agregar a lista. No es parte de la app."""

from playwright.sync_api import sync_playwright

FRONTEND = "http://localhost:5173"
OUT = "screenshots_v6"

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
        page.screenshot(path=f"{OUT}/01_empty_state.png")

        # abrir una conversacion existente con resultados
        page.click("text=Busca jefes de operaciones de")
        page.wait_for_timeout(800)
        page.screenshot(path=f"{OUT}/02_criteria_and_table.png")

        rows = page.locator("table tbody tr")
        if rows.count() > 0:
            rows.first.click()
            page.wait_for_timeout(500)
            page.screenshot(path=f"{OUT}/03_drawer.png")

            # probar crear y agregar a lista
            page.fill('input[placeholder="Nueva lista…"]', "Prospectos VIP")
            page.click("text=Crear y agregar")
            page.wait_for_timeout(1000)
            page.screenshot(path=f"{OUT}/04_list_created.png")

        browser.close()


if __name__ == "__main__":
    main()
