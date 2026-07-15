"""Interpretación de consultas en lenguaje natural -> SearchCriteria.

Prompt y reglas de clasificación validadas en backend/spike/run_interpret_spike.py:
entity_type consistente ('person' para busquedas de cargos, nunca 'professional'),
job_levels/areas separados, industries sin expandir mas alla de lo que el usuario
menciono.
"""

from openai import OpenAI
from pydantic import BaseModel, Field

from app.core.config import settings
from app.schemas.search import SearchCriteria

client = OpenAI(api_key=settings.openai_api_key)

SYSTEM_PROMPT = (
    "Eres el motor de interpretacion de Tecport Lead Intelligence, un sistema de "
    "inteligencia comercial B2B. Tu unica tarea es convertir una consulta en "
    "lenguaje natural (en espanol) sobre personas, empresas o proveedores en un "
    "criterio de busqueda estructurado. No inventes datos de contacto ni "
    "resultados: solo interpretas la intencion de busqueda del usuario.\n\n"
    "Reglas de clasificacion (obligatorias):\n"
    "- Si la consulta busca personas con un cargo (jefe, gerente, superintendente, "
    "responsable, director, coordinador, encargado, etc.), entity_type SIEMPRE es "
    "'person'. Nunca uses 'professional' para este caso.\n"
    "- Usa 'company' cuando se buscan empresas como entidad (no personas dentro de ellas).\n"
    "- Usa 'supplier' cuando se buscan proveedores de productos o servicios.\n"
    "- job_levels contiene SOLO el nivel jerarquico normalizado en espanol "
    "(jefe, gerente, superintendente, director, coordinador, responsable), sin la "
    "funcion. Ejemplo: 'jefe de operaciones' -> job_levels=['jefe'], areas=['operaciones'].\n"
    "- areas contiene la funcion o departamento (operaciones, mantenimiento, "
    "logistica, comercial, planta), separada del nivel jerarquico.\n"
    "- industries contiene UNICAMENTE el/los sectores que el usuario menciono o "
    "que se derivan directamente del tipo de empresa nombrado (ej. 'empresas "
    "portuarias' -> 'portuario'). No agregues sectores adyacentes o inferidos "
    "que el usuario no menciono.\n"
    "- Si la consulta no especifica una cantidad maxima de resultados, usa 20."
)


class CriteriaUpdate(BaseModel):
    criteria: SearchCriteria
    change_summary_es: str = Field(
        description="Explicación breve en español de qué cambió respecto al criterio anterior."
    )


def interpret(query: str) -> SearchCriteria:
    response = client.responses.parse(
        model=settings.openai_model,
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query},
        ],
        text_format=SearchCriteria,
    )
    return response.output_parsed


def refine(previous_criteria: SearchCriteria, refinement_message: str) -> CriteriaUpdate:
    user_content = (
        f"Criterio actual (JSON):\n{previous_criteria.model_dump_json(indent=2)}\n\n"
        f"El usuario ahora escribe:\n\"{refinement_message}\"\n\n"
        "Actualiza el criterio aplicando ese refinamiento. Mantén lo que no fue "
        "mencionado y modifica solo lo que el usuario pidió cambiar."
    )
    response = client.responses.parse(
        model=settings.openai_model,
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        text_format=CriteriaUpdate,
    )
    return response.output_parsed
