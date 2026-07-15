"""
Spike de interpretacion: valida si un LLM puede convertir consultas en
lenguaje natural (en espanol) sobre contactos/empresas/proveedores en criterios
estructurados, y si puede aplicar refinamientos conversacionales sobre un
criterio ya existente. No hace scraping ni guarda nada en base de datos.
"""

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from schema import CriteriaUpdate, SearchCriteria

load_dotenv()

MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

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
    "que el usuario no menciono (ej. no agregues 'logistica' o 'transporte' "
    "solo porque el sector portuario se relaciona con ellos).\n"
    "- Si la consulta no especifica una cantidad maxima de resultados, usa 20."
)

INITIAL_QUERIES = [
    "Busca jefes de operaciones de empresas portuarias en Perú",
    "Encuentra gerentes de mantenimiento de empresas mineras en Chile",
    "Busca responsables de logística de empresas industriales en Colombia",
    "Encuentra superintendentes de planta del sector cementero en Ecuador",
    "Busca gerentes comerciales de empresas de maquinaria pesada en Perú",
    "Encuentra proveedores de repuestos hidráulicos en Chile",
    "Busca empresas que vendan equipos portuarios en Perú",
]

# (consulta inicial, mensaje de refinamiento) para probar el paso 4 del flujo
REFINEMENT_CASES = [
    (
        "Busca jefes de operaciones de empresas portuarias en Perú",
        "Incluye también gerentes y superintendentes",
    ),
    (
        "Busca jefes de operaciones de empresas portuarias en Perú",
        "Solo contactos con correo y fuentes de 2025 o 2026, incluye también Chile, busca 30 resultados",
    ),
    (
        "Encuentra proveedores de repuestos hidráulicos en Chile",
        "Descarta los que no tengan sitio web ni teléfono",
    ),
]


def interpret(query: str) -> SearchCriteria:
    response = client.responses.parse(
        model=MODEL,
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
        model=MODEL,
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        text_format=CriteriaUpdate,
    )
    return response.output_parsed


def main() -> None:
    results = {"initial": [], "refinements": []}

    print("=== Interpretación de consultas iniciales ===\n")
    for query in INITIAL_QUERIES:
        criteria = interpret(query)
        print(f"> {query}")
        print(criteria.model_dump_json(indent=2))
        print()
        results["initial"].append({"query": query, "criteria": criteria.model_dump()})

    print("\n=== Refinamiento conversacional ===\n")
    for original_query, refinement_message in REFINEMENT_CASES:
        base_criteria = interpret(original_query)
        update = refine(base_criteria, refinement_message)
        print(f"> {original_query}")
        print(f">> refinamiento: {refinement_message}")
        print(f"cambio: {update.change_summary_es}")
        print(update.criteria.model_dump_json(indent=2))
        print()
        results["refinements"].append(
            {
                "original_query": original_query,
                "refinement_message": refinement_message,
                "base_criteria": base_criteria.model_dump(),
                "updated_criteria": update.criteria.model_dump(),
                "change_summary_es": update.change_summary_es,
            }
        )

    out_path = Path(__file__).parent / "spike_results.json"
    out_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nResultados guardados en {out_path}")


if __name__ == "__main__":
    main()
