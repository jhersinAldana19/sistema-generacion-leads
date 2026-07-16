"""Inserta una Search+SearchResult 'completed' de prueba directamente en la
base de datos, sin pasar por el orquestador real (evita llamadas a OpenAI y
scraping), solo para poder probar favoritos/listas en la UI. No es parte de
la app."""

import sys

from app.core.database import SessionLocal
from app.models.search import Search
from app.models.search_result import SearchResult

conversation_id = int(sys.argv[1])

db = SessionLocal()
search = Search(
    conversation_id=conversation_id,
    original_query="prueba de favoritos",
    search_type="person",
    status="completed",
    criteria_json={
        "entity_type": "person",
        "job_levels": [],
        "areas": [],
        "industries": [],
        "countries": [],
        "cities": [],
        "products_or_services": [],
        "required_contacts": [],
        "conditions": [],
        "max_results": 20,
        "summary_es": "Búsqueda de prueba",
    },
    max_results=20,
)
db.add(search)
db.commit()
db.refresh(search)

result = SearchResult(
    search_id=search.id,
    result_data_json={"full_name": "Persona de Prueba", "job_title": "Gerente de Prueba"},
    status="candidate",
    review_status="pending",
)
db.add(result)
db.commit()
db.refresh(result)

print(f"search_id={search.id} result_id={result.id}")
db.close()
