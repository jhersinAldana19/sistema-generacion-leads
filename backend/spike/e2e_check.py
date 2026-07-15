"""Verificación manual end-to-end del backend real levantado en localhost:8000.
No es parte de la app: es un script de humo para esta sesión de desarrollo."""

import time

import httpx

BASE = "http://127.0.0.1:8000"


def main() -> None:
    with httpx.Client(base_url=BASE, timeout=60) as client:
        r = client.post("/api/auth/login", json={"email": "test@tecport.com", "password": "Test1234!"})
        print("login:", r.status_code, r.json())
        assert r.status_code == 200

        r = client.post("/api/conversations", json={"title": "Prueba e2e"})
        print("conversation:", r.status_code, r.json())
        conversation_id = r.json()["id"]

        query = "Encuentra gerentes de mantenimiento de empresas mineras en Chile"
        r = client.post("/api/searches/interpret", json={"conversation_id": conversation_id, "query": query})
        print("interpret:", r.status_code)
        criteria = r.json()["criteria"]
        print(criteria)

        r = client.post("/api/searches", json={
            "conversation_id": conversation_id,
            "original_query": query,
            "criteria": criteria,
        })
        print("create search:", r.status_code, r.json())
        search_id = r.json()["id"]

        for _ in range(30):
            r = client.get(f"/api/searches/{search_id}/status")
            status_data = r.json()
            print("status:", status_data)
            if status_data["status"] in ("completed", "failed", "cancelled"):
                break
            time.sleep(5)

        r = client.get(f"/api/searches/{search_id}/results")
        results = r.json()
        print("results count:", len(results["results"]))
        for res in results["results"]:
            print(" -", res["result_data_json"].get("full_name"), "|", res["result_data_json"].get("job_title"), "|", res["result_data_json"].get("company_name"))

        if results["results"]:
            first_id = results["results"][0]["id"]
            r = client.patch(f"/api/results/{first_id}/confirm", json={})
            print("confirm:", r.status_code, r.json()["status"])

        r = client.post(f"/api/searches/{search_id}/export")
        print("export:", r.status_code, r.json())
        export_id = r.json()["export_id"]

        r = client.get(f"/api/exports/{export_id}/download")
        print("download:", r.status_code, "bytes:", len(r.content))


if __name__ == "__main__":
    main()
