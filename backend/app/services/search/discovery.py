"""Descubrimiento dinámico de empresas/URLs a partir de un criterio interpretado.

Usa la herramienta de búsqueda web nativa de OpenAI. Validado en
backend/spike/discover.py: funciona, pero en la prueba real 1 de 4 URLs
devueltas no resolvía por DNS -- por eso NINGUNA URL de aquí debe usarse sin
antes pasar por crawler.is_url_reachable() (responsabilidad del orquestador,
nunca de este módulo).
"""

import json
import re

from openai import OpenAI
from pydantic import BaseModel, Field

from app.core.config import settings
from app.schemas.search import SearchCriteria

client = OpenAI(api_key=settings.openai_api_key)


class DiscoveredCompany(BaseModel):
    name: str
    homepage_url: str = Field(description="URL real encontrada en la busqueda web, nunca inventada.")
    why_relevant_es: str


class DiscoveryResult(BaseModel):
    companies: list[DiscoveredCompany] = Field(default_factory=list)


DISCOVERY_PROMPT = (
    "Usa la herramienta de busqueda web para encontrar empresas REALES que "
    "coincidan con este criterio: {criteria}. "
    "Devuelve como maximo {max_companies} empresas distintas, con su nombre y "
    "la URL de su sitio web oficial. La URL debe provenir literalmente de un "
    "resultado de busqueda real, nunca la construyas ni la adivines. Si no "
    "encuentras suficientes empresas confiables, devuelve menos, no inventes "
    "para completar el numero.\n\n"
    "Responde UNICAMENTE con un objeto JSON con esta forma exacta, sin texto "
    "adicional antes o despues:\n"
    '{{"companies": [{{"name": "...", "homepage_url": "...", "why_relevant_es": "..."}}]}}'
)


def discover_companies(criteria: SearchCriteria, max_companies: int = 6) -> DiscoveryResult:
    prompt = DISCOVERY_PROMPT.format(
        criteria=criteria.model_dump_json(),
        max_companies=max_companies,
    )
    response = client.responses.create(
        model=settings.openai_model,
        tools=[{"type": "web_search"}],
        input=prompt,
    )
    match = re.search(r"\{.*\}", response.output_text, re.DOTALL)
    if not match:
        return DiscoveryResult(companies=[])
    return DiscoveryResult.model_validate(json.loads(match.group()))
