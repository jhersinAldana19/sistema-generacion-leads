from datetime import datetime

from pydantic import BaseModel


class SavedListCreate(BaseModel):
    name: str
    description: str | None = None


class SavedListOut(BaseModel):
    id: int
    name: str
    description: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class SavedListItemCreate(BaseModel):
    search_result_id: int
    notes: str | None = None


class SavedListItemOut(BaseModel):
    id: int
    list_id: int
    search_result_id: int
    notes: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
