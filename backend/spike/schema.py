from typing import Literal, Optional

from pydantic import BaseModel, Field

EntityType = Literal["person", "company", "supplier", "institution", "professional", "product"]
RequiredContact = Literal["email", "phone", "linkedin", "website"]


class SearchCriteria(BaseModel):
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
    summary_es: str = Field(
        description="Resumen en español de una frase de lo que se va a buscar, para mostrarlo al usuario."
    )


class CriteriaUpdate(BaseModel):
    criteria: SearchCriteria
    change_summary_es: str = Field(
        description="Explicación breve en español de qué cambió respecto al criterio anterior."
    )
