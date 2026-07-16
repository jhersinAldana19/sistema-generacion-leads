from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.conversation import Conversation
from app.models.search import Search
from app.models.search_result import SearchResult
from app.models.user import User
from app.schemas.search import (
    InterpretRequest,
    InterpretResponse,
    SearchCreateRequest,
    SearchListItemOut,
    SearchOut,
    SearchResultsOut,
    SearchStatusOut,
)
from app.services.ai.interpret import interpret, refine
from app.workers.background import enqueue_search

router = APIRouter(prefix="/api/searches", tags=["searches"])


def _get_owned_search(search_id: int, user: User, db: Session) -> Search:
    search = db.get(Search, search_id)
    if search is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Búsqueda no encontrada")
    conversation = db.get(Conversation, search.conversation_id)
    if conversation is None or conversation.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Búsqueda no encontrada")
    return search


@router.post("/interpret", response_model=InterpretResponse)
def interpret_query(
    payload: InterpretRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> InterpretResponse:
    if payload.previous_criteria is None:
        criteria = interpret(payload.query)
        return InterpretResponse(criteria=criteria, change_summary_es=None)
    update = refine(payload.previous_criteria, payload.query)
    return InterpretResponse(criteria=update.criteria, change_summary_es=update.change_summary_es)


@router.post("", response_model=SearchOut)
def create_search(
    payload: SearchCreateRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Search:
    conversation = db.get(Conversation, payload.conversation_id)
    if conversation is None or conversation.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversación no encontrada")

    search = Search(
        conversation_id=payload.conversation_id,
        original_query=payload.original_query,
        search_type=payload.criteria.entity_type,
        status="pending",
        criteria_json=payload.criteria.model_dump(),
        max_results=payload.criteria.max_results,
    )
    db.add(search)
    db.commit()
    db.refresh(search)

    enqueue_search(background_tasks, search.id)
    return search


@router.get("", response_model=list[SearchListItemOut])
def list_my_searches(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[SearchListItemOut]:
    rows = (
        db.query(Search, func.count(SearchResult.id))
        .join(Conversation, Conversation.id == Search.conversation_id)
        .outerjoin(SearchResult, SearchResult.search_id == Search.id)
        .filter(Conversation.user_id == current_user.id)
        .group_by(Search.id)
        .order_by(Search.created_at.desc())
        .limit(100)
        .all()
    )
    return [
        SearchListItemOut(
            id=search.id,
            conversation_id=search.conversation_id,
            original_query=search.original_query,
            search_type=search.search_type,
            status=search.status,
            criteria_json=search.criteria_json,
            max_results=search.max_results,
            created_at=search.created_at,
            started_at=search.started_at,
            completed_at=search.completed_at,
            error_message=search.error_message,
            result_count=count,
        )
        for search, count in rows
    ]


@router.get("/{search_id}", response_model=SearchOut)
def get_search(
    search_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Search:
    return _get_owned_search(search_id, current_user, db)


@router.get("/{search_id}/status", response_model=SearchStatusOut)
def get_search_status(
    search_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SearchStatusOut:
    search = _get_owned_search(search_id, current_user, db)
    return SearchStatusOut(id=search.id, status=search.status, progress=search.progress_json or {})


@router.get("/{search_id}/results", response_model=SearchResultsOut)
def get_search_results(
    search_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SearchResultsOut:
    search = _get_owned_search(search_id, current_user, db)
    results = db.query(SearchResult).filter(SearchResult.search_id == search_id).all()
    return SearchResultsOut(
        id=search.id,
        status=search.status,
        results=[
            {
                "id": r.id,
                "result_data_json": r.result_data_json,
                "match_score": r.match_score,
                "status": r.status,
                "review_status": r.review_status,
            }
            for r in results
        ],
    )


@router.post("/{search_id}/cancel", response_model=SearchOut)
def cancel_search(
    search_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Search:
    search = _get_owned_search(search_id, current_user, db)
    if search.status in ("pending", "running"):
        search.status = "cancelled"
        db.commit()
        db.refresh(search)
    return search
