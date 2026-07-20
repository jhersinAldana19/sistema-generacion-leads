"""Simula el bug real: una busqueda que mantiene una sesion abierta durante
mucho tiempo y a mitad de camino el pooler le mata la conexion (esto es
justo lo que hace Supabase con conexiones ociosas). Verifica que, tras el
fix, la busqueda termina en 'failed' en vez de quedar 'running' para
siempre. No es parte de la app."""

import time

from app.core.database import SessionLocal, engine
from app.models.conversation import Conversation
from app.models.search import Search
from app.models.user import User

db = SessionLocal()
user = db.query(User).first()
conversation = Conversation(user_id=user.id, title="prueba resiliencia conexion")
db.add(conversation)
db.commit()
db.refresh(conversation)
conversation_id = conversation.id

search = Search(
    conversation_id=conversation.id,
    original_query="prueba",
    search_type="person",
    status="running",
    criteria_json={"entity_type": "person"},
    progress_json={"companies_reviewed": 1, "pages_analyzed": 1, "pages_inaccessible": 1, "results_found": 0},
)
db.add(search)
db.commit()
db.refresh(search)
search_id = search.id
print(f"search creada con id={search_id}, status=running")

raw_conn = db.connection().connection.driver_connection
raw_conn.close()
print("conexion cerrada a la fuerza del lado del cliente (simulando que el pooler la corto por inactividad)")
time.sleep(1)

print("\n--- reproduciendo el flujo de run_search: commit tras la conexion muerta ---")
error_message = None
try:
    search.progress_json = {"companies_reviewed": 2, "pages_analyzed": 2, "pages_inaccessible": 1, "results_found": 0}
    db.commit()
    print("[inesperado] el commit funciono sin problema (la conexion no murio de verdad)")
except Exception as exc:
    error_message = str(exc)
    print(f"[esperado] commit fallo: {type(exc).__name__}: {error_message[:120]}")

    try:
        db.rollback()
        search.status = "failed"
        search.error_message = error_message
        db.commit()
        print("[inesperado] la sesion original se recupero sola")
    except Exception:
        print("[esperado] la sesion original sigue rota, reintentando con sesion nueva...")
        db.rollback()
        retry_db = SessionLocal()
        try:
            retry_search = retry_db.get(Search, search_id)
            retry_search.status = "failed"
            retry_search.error_message = error_message
            retry_db.commit()
            print("marcado como 'failed' con la sesion nueva")
        finally:
            retry_db.close()

db.close()

print("\n--- verificando estado final en la base de datos ---")
check_db = SessionLocal()
final = check_db.get(Search, search_id)
print(f"status final: {final.status}")
assert final.status == "failed", "el bug sigue presente: la busqueda quedo atascada"
print("\nOK: la busqueda con conexion muerta termina en 'failed', no se queda atascada")

# limpieza
check_db.delete(final)
conv = check_db.get(Conversation, conversation_id)
check_db.delete(conv)
check_db.commit()
check_db.close()
print("datos de prueba eliminados")
