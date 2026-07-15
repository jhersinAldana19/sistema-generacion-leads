from pydantic import BaseModel, Field


class ExtractedPerson(BaseModel):
    full_name: str
    job_title: str
    evidence_text: str = Field(
        description="Cita textual exacta (copiada literalmente) de la oración donde aparece esta persona y su cargo."
    )


class PageExtraction(BaseModel):
    people: list[ExtractedPerson] = Field(
        default_factory=list,
        description="Personas con nombre y cargo mencionados EXPLICITAMENTE en el texto. Lista vacia si no hay ninguna.",
    )
    notes_es: str = Field(
        description="Nota breve: por ejemplo si la pagina no tiene contenido relevante de personas/cargos."
    )
