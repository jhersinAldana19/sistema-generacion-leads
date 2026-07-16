"""Verifica: lista enriquecida (correo/telefono), clic abre detalle completo,
boton de exportar visible. No es parte de la app."""

from playwright.sync_api import sync_playwright

FRONTEND = "http://localhost:5173"
OUT = "screenshots_v10"

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

        page.click("text=Listas guardadas")
        page.wait_for_timeout(400)
        page.click("text=Prospectos VIP")
        page.wait_for_timeout(1000)
        page.screenshot(path=f"{OUT}/01_list_enriched.png")

        # clic en la persona -> debe abrir el detalle completo
        page.click("text=Antenor León León")
        page.wait_for_timeout(600)
        page.screenshot(path=f"{OUT}/02_full_detail_from_list.png")

        browser.close()


if __name__ == "__main__":
    main()
