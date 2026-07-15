"""Extracción de personas/contactos desde el texto de una página ya descargada.

Reglas anti-alucinación validadas en backend/spike/run_extract_spike*.py:
- El LLM solo puede reportar personas cuyo nombre Y cargo aparezcan
  explícitamente en el texto entregado, con evidencia textual literal.
- Si Trafilatura entrega poco texto (posible layout de "tarjetas"), se usa
  también el texto de respaldo (encabezados+párrafos) para no perder nombres
  reales que Trafilatura descarta como boilerplate.
"""

from datetime import datetime, timezone

import trafilatura
from openai import OpenAI
from pydantic import BaseModel, Field

from app.core.config import settings
from app.services.scraping.crawler import (
    extract_emails,
    extract_headings_and_paragraphs,
    extract_phones_from_clean_text,
    extract_tel_links,
)

client = OpenAI(api_key=settings.openai_api_key)

MIN_TEXT_LENGTH_FOR_LLM = 200
FALLBACK_TRIGGER_LENGTH = 400  # si Trafilatura da menos que esto, probamos el texto de respaldo


class ExtractedPerson(BaseModel):
    full_name: str
    job_title: str = Field(
        description="Nunca vacío: si el texto no menciona un cargo explícito para esta persona, no la incluyas en people."
    )
    evidence_text: str = Field(
        description="Cita textual exacta (copiada literalmente) de la oración donde aparece esta persona y su cargo."
    )


class PageExtraction(BaseModel):
    people: list[ExtractedPerson] = Field(default_factory=list)
    notes_es: str = Field(default="")


SYSTEM_PROMPT = (
    "Extraes personas mencionadas con nombre y cargo en un texto proveniente de "
    "un sitio corporativo real. Reglas estrictas: "
    "1) Solo incluye personas cuyo nombre completo Y cargo aparezcan explicitamente "
    "escritos en el texto. Si encuentras un nombre junto a un correo o telefono pero "
    "SIN ningun cargo/puesto mencionado (ej. una lista de contactos de un equipo de "
    "ventas o soporte), NO la incluyas en people, sin importar que el dato de "
    "contacto se vea real. "
    "2) No inventes ni infieras nombres, cargos, ni relaciones entre nombre y cargo "
    "que no esten escritas literalmente. "
    "3) Copia la evidencia textual exacta (verbatim) del fragmento del texto original. "
    "4) Si el texto no contiene ninguna persona con nombre Y cargo explicitos, "
    "devuelve una lista vacia y explica brevemente por que en notes_es. "
    "5) No proceses el texto como si fuera de otra empresa: usa solo lo dado."
)


def _llm_extract_people(text: str, url: str) -> PageExtraction:
    response = client.responses.parse(
        model=settings.openai_model,
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"URL fuente: {url}\n\nTEXTO:\n{text[:8000]}"},
        ],
        text_format=PageExtraction,
    )
    return response.output_parsed


def extract_page(url: str, html: str) -> dict:
    """Devuelve un dict con emails, phones, people (con evidencia) y metadatos
    de fuente para una página ya descargada."""
    retrieved_at = datetime.now(timezone.utc).isoformat()

    clean_text = trafilatura.extract(html, url=url, include_comments=False, include_tables=False) or ""
    text_for_llm = clean_text
    used_fallback = False
    if len(clean_text) < FALLBACK_TRIGGER_LENGTH:
        fallback_text = extract_headings_and_paragraphs(html)
        if len(fallback_text) > len(clean_text):
            text_for_llm = fallback_text
            used_fallback = True

    emails = extract_emails(clean_text) or extract_emails(html)
    phones = sorted(set(extract_tel_links(html)) | set(extract_phones_from_clean_text(clean_text)))

    people: list[dict] = []
    notes_es = "Texto insuficiente para analizar."
    if len(text_for_llm) >= MIN_TEXT_LENGTH_FOR_LLM:
        extraction = _llm_extract_people(text_for_llm, url)
        people = [p.model_dump() for p in extraction.people]
        notes_es = extraction.notes_es

    return {
        "url": url,
        "retrieved_at": retrieved_at,
        "used_fallback_text": used_fallback,
        "emails_found": emails,
        "phones_found": phones,
        "people_found": people,
        "notes_es": notes_es,
    }
