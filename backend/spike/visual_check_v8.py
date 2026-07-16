"""Verificacion final: prueba cada conversacion del historial hasta encontrar
la que tiene resultados reales, con espera mas generosa. No es parte de la app."""

from playwright.sync_api import sync_playwright

FRONTEND = "http://localhost:5173"
OUT = "screenshots_v8"

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

        conv_buttons = page.locator("aside p:text('HISTORIAL') ~ ul button")
        count = conv_buttons.count()
        print("conversaciones:", count)

        for i in range(count):
            page.locator("aside p:text('HISTORIAL') ~ ul button").nth(i).click()
            page.wait_for_timeout(2500)
            rows = page.locator("table tbody tr")
            n = rows.count()
            print(f"conversacion #{i}: {n} filas")
            if n > 0:
                page.screenshot(path=f"{OUT}/table_conv{i}.png")
                rows.first.click()
                page.wait_for_timeout(600)
                page.screenshot(path=f"{OUT}/drawer_conv{i}.png")

                page.fill('input[placeholder="Nueva lista…"]', "Prospectos VIP")
                page.click("text=Crear y agregar")
                page.wait_for_timeout(1200)
                page.screenshot(path=f"{OUT}/list_feedback_conv{i}.png")
                break

        browser.close()


if __name__ == "__main__":
    main()
