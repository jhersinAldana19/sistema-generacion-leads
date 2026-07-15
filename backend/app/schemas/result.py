from datetime import datetime

from pydantic import BaseModel


class ResultOut(BaseModel):
    id: int
    search_id: int
    result_data_json: dict
    match_score: float | None = None
    status: str
    review_status: str
    created_at: datetime
    reviewed_at: datetime | None = None

    model_config = {"from_attributes": True}


class ResultReviewUpdate(BaseModel):
    notes: str | None = None
