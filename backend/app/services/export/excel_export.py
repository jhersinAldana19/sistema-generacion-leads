"""Exportación a Excel. El pipeline actual nunca genera contactos 'inferred'
(solo direct_published/company_general/not_found), así que no hace falta un
filtro adicional para no exportarlos como verificados -- si en el futuro se
agrega inferencia de patrones de correo, este exportador deberá excluir
explícitamente cualquier contact_type == 'inferred'.
"""

from pathlib import Path

import pandas as pd

from app.core.config import settings

STATUS_ES = {
    "candidate": "Candidato",
    "probable": "Probable",
    "confirmed": "Confirmado",
    "outdated": "Fuente antigua",
    "needs_review": "Requiere revisión",
    "discarded": "Descartado",
}

COLUMNS = [
    ("full_name", "Nombre"),
    ("job_title", "Cargo"),
    ("area", "Área"),
    ("company_name", "Empresa"),
    ("industry", "Sector"),
    ("country", "País"),
    ("city", "Ciudad"),
    ("direct_email", "Correo directo"),
    ("direct_email_type", "Tipo de correo"),
    ("company_email", "Correo corporativo"),
    ("direct_phone", "Teléfono directo"),
    ("direct_phone_type", "Tipo de teléfono"),
    ("company_phone", "Teléfono de empresa"),
    ("linkedin_url", "LinkedIn"),
    ("source_url", "Fuente"),
    ("source_date", "Fecha de la fuente"),
    ("evidence_text", "Evidencia"),
]


def build_export_dataframe(results: list[dict]) -> pd.DataFrame:
    rows = []
    for result in results:
        data = result["result_data_json"]
        row = {label: data.get(key) for key, label in COLUMNS}
        row["Estado"] = STATUS_ES.get(result["status"], result["status"])
        row["Campos faltantes"] = ", ".join(data.get("missing_fields") or [])
        rows.append(row)
    return pd.DataFrame(rows)


def export_search_to_excel(search_id: int, results: list[dict], file_name: str) -> str:
    export_dir = Path(settings.export_directory)
    export_dir.mkdir(parents=True, exist_ok=True)
    file_path = export_dir / file_name

    df = build_export_dataframe(results)
    summary = df["Estado"].value_counts().rename_axis("Estado").reset_index(name="Cantidad") if not df.empty else pd.DataFrame(columns=["Estado", "Cantidad"])

    with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Resultados", index=False)
        summary.to_excel(writer, sheet_name="Resumen", index=False)

    return str(file_path)
