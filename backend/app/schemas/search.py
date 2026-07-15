from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

EntityType = Literal["person", "company", "supplier", "institution", "professional", "product"]
RequiredContact = Literal["email", "phone", "linkedin", "website"]


class SearchCriteria(BaseModel):
    """Criterio de búsqueda interpretado. Misma forma validada en backend/spike/schema.py."""

    entity_type: EntityType
    job_levels: list[str] = Field(default_factory=list)
    areas: list[str] = Field(default_factory=list)
    industries: list[str] = Field(default_factory=list)
    countries: list[str] = Field(default_factory=list)
    cities: list[str] = Field(default_factory=list)
    products_or_services: list[str] = Field(default_factory=list)
    required_contacts: list[RequiredContact] = Field(default_factory=list)
    conditions: list[str] = Field(default_factory=list)
    max_results: int = 20
    summary_es: str


class InterpretRequest(BaseModel):
    conversation_id: int
    query: str
    previous_criteria: SearchCriteria | None = None


class InterpretResponse(BaseModel):
    criteria: SearchCriteria
    change_summary_es: str | None = None


class SearchCreateRequest(BaseModel):
    conversation_id: int
    original_query: str
    criteria: SearchCriteria


class SearchOut(BaseModel):
    id: int
    conversation_id: int
    original_query: str
    search_type: str
    status: str
    criteria_json: dict
    max_results: int
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    error_message: str | None = None

    model_config = {"from_attributes": True}


class SearchStatusOut(BaseModel):
    id: int
    status: str
    progress: dict


class SearchResultsOut(BaseModel):
    id: int
    status: str
    results: list[dict]
