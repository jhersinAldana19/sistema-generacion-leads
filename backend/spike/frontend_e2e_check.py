"""Smoke test de UI real (Playwright) contra el frontend en localhost:5173 y el
backend en localhost:8000. No es parte de la app: verificación manual de esta
sesión de desarrollo."""

from playwright.sync_api import sync_playwright

FRONTEND = "http://localhost:5173"
SCREENSHOT_DIR = "screenshots"

import os
os.makedirs(SCREENSHOT_DIR, exist_ok=True)


def main() -> None:
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page()
        page.on("console", lambda msg: print(f"[console:{msg.type}] {msg.text}"))
        page.on("pageerror", lambda exc: print(f"[pageerror] {exc}"))

        page.goto(FRONTEND)
        page.wait_for_timeout(500)
        page.screenshot(path=f"{SCREENSHOT_DIR}/01_login.png")
        print("URL tras cargar:", page.url)

        page.fill("#email", "test@tecport.com")
        page.fill("#password", "Test1234!")
        page.click("button[type=submit]")
        page.wait_for_url(f"{FRONTEND}/", timeout=10000)
        page.wait_for_timeout(1000)
        page.screenshot(path=f"{SCREENSHOT_DIR}/02_chat_empty.png")
        print("Login OK, URL:", page.url)

        page.click("text=Nueva conversación")
        page.wait_for_timeout(1000)
        page.screenshot(path=f"{SCREENSHOT_DIR}/03_new_conversation.png")

        composer = page.locator("textarea")
        composer.fill("Encuentra gerentes de mantenimiento de empresas mineras en Chile")
        composer.press("Enter")

        page.wait_for_selector("text=Entendí tu búsqueda", timeout=20000)
        page.screenshot(path=f"{SCREENSHOT_DIR}/04_criteria_card.png")
        print("CriteriaCard visible")

        page.click("text=Iniciar búsqueda")
        page.wait_for_timeout(1000)
        page.screenshot(path=f"{SCREENSHOT_DIR}/05_progress.png")
        print("Busqueda iniciada, esperando progreso...")

        import time

        deadline = time.time() + 120
        final_text = None
        while time.time() < deadline:
            for candidate in ("Búsqueda completa", "La búsqueda tuvo un error", "Búsqueda cancelada"):
                if page.locator(f"text={candidate}").count() > 0:
                    final_text = candidate
                    break
            if final_text:
                break
            page.wait_for_timeout(2000)
        print("Estado final de texto encontrado:", final_text)
        page.wait_for_timeout(1000)
        page.screenshot(path=f"{SCREENSHOT_DIR}/06_results_or_error.png")
        print("Estado final alcanzado")

        rows = page.locator("table tbody tr")
        count = rows.count()
        print("Filas de resultados:", count)
        if count > 0:
            rows.first.click()
            page.wait_for_timeout(500)
            page.screenshot(path=f"{SCREENSHOT_DIR}/07_drawer.png")
            print("Drawer abierto")

        browser.close()


if __name__ == "__main__":
    main()
