"""
Spike de descubrimiento: a partir de un criterio de busqueda YA interpretado
(no hardcodeado a mano), usa la herramienta de busqueda web nativa de OpenAI
para encontrar empresas reales y sus sitios web, sin inventar URLs.
Esta es la pieza que le faltaba al pipeline para funcionar con CUALQUIER
consulta, no solo con las empresas que elegi manualmente para el spike de
extraccion.
"""

import os

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

from schema import SearchCriteria

load_dotenv()
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")


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


def discover_companies(criteria: SearchCriteria, max_companies: int = 4) -> DiscoveryResult:
    prompt = DISCOVERY_PROMPT.format(
        criteria=criteria.model_dump_json(),
        max_companies=max_companies,
    )
    response = client.responses.create(
        model=MODEL,
        tools=[{"type": "web_search"}],
        input=prompt,
    )
    # El SDK no soporta tools + parse estructurado a la vez en esta version,
    # asi que se pide JSON explicito y se valida con Pydantic manualmente.
    text = response.output_text
    import json
    import re

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError(f"No se encontro JSON en la respuesta: {text}")
    return DiscoveryResult.model_validate(json.loads(match.group()))


if __name__ == "__main__":
    from run_interpret_spike import interpret

    query = "Encuentra gerentes de mantenimiento de empresas mineras en Chile"
    criteria = interpret(query)
    print(f"Criterio interpretado: {criteria.model_dump_json(indent=2)}\n")

    result = discover_companies(criteria)
    for company in result.companies:
        print(f"- {company.name}: {company.homepage_url}")
        print(f"  motivo: {company.why_relevant_es}")
