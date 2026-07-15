"""Verificacion visual de branding + modo oscuro. No es parte de la app."""

from playwright.sync_api import sync_playwright

FRONTEND = "http://localhost:5173"
OUT = "screenshots_v2"

import os
os.makedirs(OUT, exist_ok=True)


def main() -> None:
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.on("pageerror", lambda exc: print(f"[pageerror] {exc}"))

        page.goto(FRONTEND)
        page.wait_for_timeout(1500)
        page.screenshot(path=f"{OUT}/01_login.png")
        print("login screenshot ok")

        page.fill("#email", "test@tecport.com")
        page.fill("#password", "Test1234!")
        page.click("button[type=submit]")
        page.wait_for_url(f"{FRONTEND}/", timeout=10000)
        page.wait_for_timeout(1500)
        page.screenshot(path=f"{OUT}/02_chat_light.png")
        print("chat light screenshot ok")

        # click theme toggle (in sidebar)
        page.click('button[aria-label*="oscuro"]')
        page.wait_for_timeout(500)
        page.screenshot(path=f"{OUT}/03_chat_dark.png")
        print("chat dark screenshot ok")

        # open a conversation with content if exists, to see cards in dark mode
        conv_buttons = page.locator("aside button, aside >> text=Prueba")
        print("sidebar conv candidates:", conv_buttons.count())

        browser.close()


if __name__ == "__main__":
    main()
