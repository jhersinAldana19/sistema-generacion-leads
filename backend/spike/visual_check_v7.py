"""Verifica avatares en tabla + drawer + flujo de crear-y-agregar a lista,
usando la conversacion con resultados reales ya completados (la ultima del
historial). No es parte de la app."""

from playwright.sync_api import sync_playwright

FRONTEND = "http://localhost:5173"
OUT = "screenshots_v7"

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

        # la conversacion completada es la ultima del historial (mas antigua)
        conv_buttons = page.locator("aside p:text('HISTORIAL') ~ ul button")
        print("conversaciones encontradas:", conv_buttons.count())
        conv_buttons.last.click()
        page.wait_for_timeout(1000)
        page.screenshot(path=f"{OUT}/01_table_with_avatars.png")

        rows = page.locator("table tbody tr")
        print("filas:", rows.count())
        if rows.count() > 0:
            rows.first.click()
            page.wait_for_timeout(500)
            page.screenshot(path=f"{OUT}/02_drawer.png")

            page.fill('input[placeholder="Nueva lista…"]', "Prospectos VIP")
            page.click("text=Crear y agregar")
            page.wait_for_timeout(1200)
            page.screenshot(path=f"{OUT}/03_list_created_feedback.png")

        browser.close()


if __name__ == "__main__":
    main()
