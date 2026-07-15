"""Verificacion de los 4 fixes: altura del login, tamano de logo, tema claro
por defecto, centrado del estado vacio. No es parte de la app."""

from playwright.sync_api import sync_playwright

FRONTEND = "http://localhost:5173"
OUT = "screenshots_v3"

import os
os.makedirs(OUT, exist_ok=True)


def main() -> None:
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.on("pageerror", lambda exc: print(f"[pageerror] {exc}"))

        page.goto(FRONTEND)
        page.wait_for_timeout(1500)

        # medir si la pagina de login requiere scroll
        scroll_height = page.evaluate("document.documentElement.scrollHeight")
        client_height = page.evaluate("document.documentElement.clientHeight")
        print(f"login scrollHeight={scroll_height} clientHeight={client_height} (deberian ser iguales)")
        page.screenshot(path=f"{OUT}/01_login.png")

        page.fill("#email", "test@tecport.com")
        page.fill("#password", "Test1234!")
        page.click("button[type=submit]")
        page.wait_for_url(f"{FRONTEND}/", timeout=10000)
        page.wait_for_timeout(1000)

        is_dark_by_default = page.evaluate("document.documentElement.classList.contains('dark')")
        print("modo oscuro activo por defecto?:", is_dark_by_default)
        page.screenshot(path=f"{OUT}/02_after_login_default_theme.png")

        # crear nueva conversacion vacia y revisar centrado
        page.click("text=Nueva conversación")
        page.wait_for_timeout(800)
        page.screenshot(path=f"{OUT}/03_empty_conversation_centered.png")

        browser.close()


if __name__ == "__main__":
    main()
