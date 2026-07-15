from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.saved_list import SavedList, SavedListItem
from app.models.user import User
from app.schemas.lists import SavedListCreate, SavedListItemCreate, SavedListItemOut, SavedListOut

router = APIRouter(prefix="/api/lists", tags=["lists"])


def _get_owned_list(list_id: int, user: User, db: Session) -> SavedList:
    saved_list = db.get(SavedList, list_id)
    if saved_list is None or saved_list.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lista no encontrada")
    return saved_list


@router.post("", response_model=SavedListOut)
def create_list(
    payload: SavedListCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SavedList:
    saved_list = SavedList(user_id=current_user.id, name=payload.name, description=payload.description)
    db.add(saved_list)
    db.commit()
    db.refresh(saved_list)
    return saved_list


@router.get("", response_model=list[SavedListOut])
def list_lists(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[SavedList]:
    return db.query(SavedList).filter(SavedList.user_id == current_user.id).all()


@router.post("/{list_id}/items", response_model=SavedListItemOut)
def add_item(
    list_id: int,
    payload: SavedListItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SavedListItem:
    _get_owned_list(list_id, current_user, db)
    item = SavedListItem(list_id=list_id, search_result_id=payload.search_result_id, notes=payload.notes)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{list_id}/items/{item_id}")
def remove_item(
    list_id: int,
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    _get_owned_list(list_id, current_user, db)
    item = db.get(SavedListItem, item_id)
    if item is None or item.list_id != list_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Elemento no encontrado")
    db.delete(item)
    db.commit()
    return {"ok": True}
