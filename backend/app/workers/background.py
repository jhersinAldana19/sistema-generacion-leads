"""Punto único para lanzar trabajo en segundo plano. MVP: BackgroundTasks de
FastAPI (sin Celery/Redis, tal como pide el alcance del proyecto)."""

from fastapi import BackgroundTasks

from app.services.search_orchestrator import run_search


def enqueue_search(background_tasks: BackgroundTasks, search_id: int) -> None:
    background_tasks.add_task(run_search, search_id)
