from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.base import utcnow
from app.models.conversation import Conversation
from app.models.search import Search
from app.models.search_result import SearchResult
from app.models.user import User
from app.schemas.result import ResultOut, ResultReviewUpdate

router = APIRouter(prefix="/api/results", tags=["results"])


def _get_owned_result(result_id: int, user: User, db: Session) -> SearchResult:
    result = db.get(SearchResult, result_id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resultado no encontrado")
    search = db.get(Search, result.search_id)
    conversation = db.get(Conversation, search.conversation_id) if search else None
    if conversation is None or conversation.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resultado no encontrado")
    return result


@router.get("/{result_id}", response_model=ResultOut)
def get_result(
    result_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SearchResult:
    return _get_owned_result(result_id, current_user, db)


@router.patch("/{result_id}/confirm", response_model=ResultOut)
def confirm_result(
    result_id: int,
    payload: ResultReviewUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SearchResult:
    result = _get_owned_result(result_id, current_user, db)
    result.status = "confirmed"
    result.review_status = "confirmed"
    result.reviewed_at = utcnow()
    result.reviewed_by = current_user.id
    db.commit()
    db.refresh(result)
    return result


@router.patch("/{result_id}/discard", response_model=ResultOut)
def discard_result(
    result_id: int,
    payload: ResultReviewUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SearchResult:
    result = _get_owned_result(result_id, current_user, db)
    result.status = "discarded"
    result.review_status = "discarded"
    result.reviewed_at = utcnow()
    result.reviewed_by = current_user.id
    db.commit()
    db.refresh(result)
    return result


@router.patch("/{result_id}/review", response_model=ResultOut)
def flag_result_for_review(
    result_id: int,
    payload: ResultReviewUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SearchResult:
    result = _get_owned_result(result_id, current_user, db)
    result.status = "needs_review"
    result.review_status = "flagged"
    result.reviewed_at = utcnow()
    result.reviewed_by = current_user.id
    db.commit()
    db.refresh(result)
    return result
