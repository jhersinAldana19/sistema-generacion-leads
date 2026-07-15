"""Prueba minima: ¿el SDK/modelo instalado soporta la herramienta de busqueda
web nativa de OpenAI? Si falla, hay que usar una API de busqueda externa."""

import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

try:
    response = client.responses.create(
        model=MODEL,
        tools=[{"type": "web_search"}],
        input="¿Cual es el sitio web oficial de la empresa minera Antamina en Peru? Responde solo la URL.",
    )
    print("EXITO con tool 'web_search'")
    print(response.output_text)
except Exception as exc:
    print(f"Fallo 'web_search': {exc}")
    try:
        response = client.responses.create(
            model=MODEL,
            tools=[{"type": "web_search_preview"}],
            input="¿Cual es el sitio web oficial de la empresa minera Antamina en Peru? Responde solo la URL.",
        )
        print("EXITO con tool 'web_search_preview'")
        print(response.output_text)
    except Exception as exc2:
        print(f"Fallo 'web_search_preview' tambien: {exc2}")
