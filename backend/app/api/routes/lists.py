from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.saved_list import SavedList, SavedListItem
from app.models.search_result import SearchResult
from app.models.user import User
from app.schemas.lists import (
    SavedListCreate,
    SavedListItemCreate,
    SavedListItemDetailOut,
    SavedListItemOut,
    SavedListOut,
)
from app.services.export.excel_export import export_search_to_excel

router = APIRouter(prefix="/api/lists", tags=["lists"])


def _get_owned_list(list_id: int, user: User, db: Session) -> SavedList:
    saved_list = db.get(SavedList, list_id)
    if saved_list is None or saved_list.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lista no encontrada")
    return saved_list


def _get_list_rows(list_id: int, db: Session) -> list[tuple[SavedListItem, SearchResult]]:
    return (
        db.query(SavedListItem, SearchResult)
        .join(SearchResult, SearchResult.id == SavedListItem.search_result_id)
        .filter(SavedListItem.list_id == list_id)
        .order_by(SavedListItem.created_at.desc())
        .all()
    )


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


@router.get("/{list_id}/items", response_model=list[SavedListItemDetailOut])
def list_items(
    list_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[SavedListItemDetailOut]:
    _get_owned_list(list_id, current_user, db)
    rows = _get_list_rows(list_id, db)
    return [
        SavedListItemDetailOut(
            id=item.id,
            list_id=item.list_id,
            search_result_id=item.search_result_id,
            notes=item.notes,
            created_at=item.created_at,
            result_data_json=result.result_data_json,
            result_status=result.status,
        )
        for item, result in rows
    ]


@router.get("/{list_id}/export")
def export_list(
    list_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FileResponse:
    saved_list = _get_owned_list(list_id, current_user, db)
    rows = _get_list_rows(list_id, db)
    results_dicts = [{"result_data_json": result.result_data_json, "status": result.status} for _, result in rows]

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = "".join(c if c.isalnum() else "_" for c in saved_list.name).strip("_") or "lista"
    file_name = f"lista_{safe_name}_{timestamp}.xlsx"
    file_path = export_search_to_excel(list_id, results_dicts, file_name)

    return FileResponse(
        path=file_path,
        filename=file_name,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


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
