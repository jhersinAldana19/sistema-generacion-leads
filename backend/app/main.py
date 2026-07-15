from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, conversations, exports, lists, results, searches
from app.core.config import settings

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(conversations.router)
app.include_router(searches.router)
app.include_router(results.router)
app.include_router(lists.router)
app.include_router(exports.router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "app": settings.app_name}
