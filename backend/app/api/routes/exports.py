from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.conversation import Conversation
from app.models.export import Export
from app.models.search import Search
from app.models.search_result import SearchResult
from app.models.user import User
from app.services.export.excel_export import export_search_to_excel

router = APIRouter(tags=["exports"])


@router.post("/api/searches/{search_id}/export")
def export_search(
    search_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    search = db.get(Search, search_id)
    if search is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Búsqueda no encontrada")
    conversation = db.get(Conversation, search.conversation_id)
    if conversation is None or conversation.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Búsqueda no encontrada")

    results = db.query(SearchResult).filter(SearchResult.search_id == search_id).all()
    results_dicts = [{"result_data_json": r.result_data_json, "status": r.status} for r in results]

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"busqueda_{search_id}_{timestamp}.xlsx"
    file_path = export_search_to_excel(search_id, results_dicts, file_name)

    export_record = Export(
        search_id=search_id,
        user_id=current_user.id,
        file_name=file_name,
        file_path=file_path,
    )
    db.add(export_record)
    db.commit()
    db.refresh(export_record)

    return {"export_id": export_record.id, "file_name": file_name}


@router.get("/api/exports/{export_id}/download")
def download_export(
    export_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FileResponse:
    export_record = db.get(Export, export_id)
    if export_record is None or export_record.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exportación no encontrada")
    return FileResponse(
        path=export_record.file_path,
        filename=export_record.file_name,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
