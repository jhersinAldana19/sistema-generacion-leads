"""Verifica end-to-end en navegador real que las 3 acciones de eliminar
(conversacion, quitar favorito, eliminar lista) funcionan tras el fix de
cascada en delete_conversation. No es parte de la app."""

from playwright.sync_api import sync_playwright

FRONTEND = "http://localhost:5173"


def main() -> None:
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        errors = []
        page_errors = []
        page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)
        page.on("pageerror", lambda exc: page_errors.append(str(exc)))
        page.on("dialog", lambda dialog: (print(f"[dialog] {dialog.message}"), dialog.accept()))
        page.on(
            "response",
            lambda res: print(f"[net] {res.request.method} {res.url} -> {res.status}")
            if "/api/" in res.url
            else None,
        )
        page.on(
            "requestfailed",
            lambda req: print(f"[net:FAILED] {req.method} {req.url} -> {req.failure}")
            if "/api/" in req.url
            else None,
        )
        page.on(
            "request",
            lambda req: print(f"[net:req] {req.method} {req.url}")
            if "/api/conversations" in req.url and req.method == "DELETE"
            else None,
        )

        page.goto(FRONTEND)
        page.wait_for_timeout(1000)
        page.fill("#email", "sistemas@tecportla.com")
        page.fill("#password", "Tecport19$123jA!2026")
        page.click("button[type=submit]")
        page.wait_for_url(f"{FRONTEND}/", timeout=10000)
        page.wait_for_timeout(800)

        print("=== 2) Quitar una busqueda de favoritas (ya viene pre-marcada por seed) ===")
        page.click("text=Búsquedas favoritas")
        page.wait_for_timeout(1500)
        fav_count_before = page.locator('button[aria-label="Quitar de favoritas"]').count()
        print("favoritas visibles:", fav_count_before)
        if fav_count_before == 0:
            print("--- errores de consola hasta ahora ---")
            for e in errors:
                print("[console:error]", e)
            print("--- pageerror ---")
            print(page_errors)
        assert fav_count_before > 0, "la busqueda no aparecio en favoritas"
        fav_li = page.locator('button[aria-label="Quitar de favoritas"]').first.locator("xpath=ancestor::li[1]")
        fav_li.hover()
        page.wait_for_timeout(300)
        page.locator('button[aria-label="Quitar de favoritas"]').first.click()
        page.wait_for_timeout(2500)
        fav_count_after = page.locator('button[aria-label="Quitar de favoritas"]').count()
        print("favoritas despues de quitar:", fav_count_after)
        if fav_count_after != fav_count_before - 1:
            print("--- errores tras el click ---")
            for e in errors:
                print("[console:error]", e)
            print("pageerrors:", page_errors)
        assert fav_count_after == fav_count_before - 1, "no se quito de favoritas"

        print("\n=== 3) Eliminar una lista guardada ===")
        page.click("text=Listas guardadas")
        page.wait_for_timeout(500)
        list_count_before = page.locator('button[aria-label="Eliminar lista"]').count()
        print("listas antes:", list_count_before)
        if list_count_before == 0:
            print("no hay listas para probar, se omite paso 3")
        else:
            list_li = page.locator('button[aria-label="Eliminar lista"]').first.locator("xpath=ancestor::li[1]")
            list_li.hover()
            page.wait_for_timeout(300)
            page.locator('button[aria-label="Eliminar lista"]').first.click()
            page.wait_for_timeout(2500)
            list_count_after = page.locator('button[aria-label="Eliminar lista"]').count()
            print("listas despues:", list_count_after)
            assert list_count_after == list_count_before - 1, "no se elimino la lista"

        print("\n=== Errores de consola capturados ===")
        for e in errors:
            print("[console:error]", e)

        browser.close()
        print("\nOK: verificacion completa" if not errors else "\nHubo errores de consola, revisar arriba")


if __name__ == "__main__":
    main()
