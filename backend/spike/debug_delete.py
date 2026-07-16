"""Diagnostico de por que los botones de eliminar no funcionan. Captura la
consola del navegador y las respuestas de red para las 3 acciones.
No es parte de la app."""

from playwright.sync_api import sync_playwright

FRONTEND = "http://localhost:5173"


def main() -> None:
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.on("console", lambda msg: print(f"[console:{msg.type}] {msg.text}"))
        page.on("pageerror", lambda exc: print(f"[pageerror] {exc}"))
        page.on(
            "response",
            lambda res: print(f"[net] {res.request.method} {res.url} -> {res.status}")
            if "/api/" in res.url
            else None,
        )
        page.on("dialog", lambda dialog: (print(f"[dialog] {dialog.message}"), dialog.accept()))

        page.goto(FRONTEND)
        page.wait_for_timeout(1000)
        page.fill("#email", "sistemas@tecportla.com")
        page.fill("#password", "Tecport19$123jA!2026")
        page.click("button[type=submit]")
        page.wait_for_url(f"{FRONTEND}/", timeout=10000)
        page.wait_for_timeout(800)

        print("\n=== Intentando eliminar una conversacion del Historial ===")
        conv_item = page.locator("aside p:text('HISTORIAL') ~ ul li").first
        conv_item.hover()
        page.wait_for_timeout(300)
        trash_in_conv = conv_item.locator('span[role="button"]').last
        print("trash visible?", trash_in_conv.is_visible())
        trash_in_conv.click(force=True)
        page.wait_for_timeout(1000)

        print("\n=== Intentando eliminar/desmarcar una busqueda favorita ===")
        page.click("text=Búsquedas favoritas")
        page.wait_for_timeout(500)
        fav_item = page.locator("aside p:text('BÚSQUEDAS FAVORITAS') ~ ul li, aside button:text('Búsquedas favoritas') ~ ul li").first
        if fav_item.count() == 0:
            fav_item = page.locator("li", has_text="resultado(s)").first
        fav_item.hover()
        page.wait_for_timeout(300)
        trash_btn = fav_item.locator('button[aria-label="Quitar de favoritas"]')
        print("fav trash count:", trash_btn.count())
        if trash_btn.count() > 0:
            trash_btn.click(force=True)
            page.wait_for_timeout(1000)

        print("\n=== Intentando eliminar una lista guardada ===")
        page.click("text=Listas guardadas")
        page.wait_for_timeout(500)
        list_item = page.locator("li", has_text="nueva").first
        list_item.hover()
        page.wait_for_timeout(300)
        list_trash = list_item.locator('button[aria-label="Eliminar lista"]')
        print("list trash count:", list_trash.count())
        if list_trash.count() > 0:
            list_trash.click(force=True)
            page.wait_for_timeout(1000)

        browser.close()


if __name__ == "__main__":
    main()
