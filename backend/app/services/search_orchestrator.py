"""Orquesta una búsqueda completa: pending -> running -> completed/failed.

Encadena las piezas ya validadas por separado en backend/spike/:
interpretación (ya hecha antes de crear la Search) -> discovery -> verificación
obligatoria de cada URL -> crawler -> extractor -> persistencia de resultados.
Sin Celery/Redis: se ejecuta como BackgroundTask de FastAPI (ver app/workers/background.py).
"""

from urllib.parse import urlparse

import httpx

from app.core.database import SessionLocal
from app.core.config import settings
from app.models.base import utcnow
from app.models.search import Search
from app.models.search_result import SearchResult
from app.schemas.search import SearchCriteria
from app.services.extraction.extractor import extract_page
from app.services.scraping.crawler import (
    CANDIDATE_KEYWORDS,
    INVESTOR_KEYWORDS,
    discover_candidate_links,
    fetch,
    is_url_reachable,
)
from app.services.search.discovery import discover_companies

GENERIC_EMAIL_PREFIXES = {"contacto", "info", "ventas", "sales", "comercial", "contact", "hola", "informacion"}


def _is_generic_email(email: str) -> bool:
    local_part = email.split("@")[0].lower()
    return local_part in GENERIC_EMAIL_PREFIXES or "." not in local_part


def _build_result_data(
    person: dict,
    company_name: str,
    page_url: str,
    criteria: SearchCriteria,
    page_emails: list[str],
    page_phones: list[str],
) -> dict:
    """Arma el JSON de resultado con la forma del ejemplo de persona del spec.
    Solo empareja un email/telefono directo con la persona cuando hay exactamente
    1 dato "no generico" en la pagina -- si hay ambigüedad (0 o 2+), se deja en
    null en vez de adivinar a quien pertenece (regla: no inventar)."""

    generic_emails = [e for e in page_emails if _is_generic_email(e)]
    personal_emails = [e for e in page_emails if not _is_generic_email(e)]

    direct_email = personal_emails[0] if len(personal_emails) == 1 else None
    company_email = generic_emails[0] if generic_emails else (page_emails[0] if page_emails and not direct_email else None)

    direct_phone = page_phones[0] if len(page_phones) == 1 else None
    company_phone = page_phones[0] if page_phones and direct_phone is None else None

    parsed = urlparse(page_url)
    company_website = f"{parsed.scheme}://{parsed.netloc}" if parsed.netloc else None

    missing_fields = [
        field for field, value in [
            ("direct_email", direct_email),
            ("direct_phone", direct_phone),
            ("linkedin_url", None),
            ("city", None),
            ("source_date", None),
        ]
        if value is None
    ]

    return {
        "entity_type": "person",
        "full_name": person["full_name"],
        "job_title": person["job_title"],
        "area": criteria.areas[0] if criteria.areas else None,
        "company_name": company_name,
        "industry": criteria.industries[0] if criteria.industries else None,
        "country": criteria.countries[0] if criteria.countries else None,
        "city": None,
        "linkedin_url": None,
        "direct_email": direct_email,
        "direct_email_type": "direct_published" if direct_email else None,
        "direct_email_status": "published" if direct_email else None,
        "direct_phone": direct_phone,
        "direct_phone_type": "phone_direct" if direct_phone else None,
        "company_email": company_email,
        "company_phone": company_phone,
        "company_website": company_website,
        "source_url": page_url,
        "source_date": None,
        "evidence_text": person["evidence_text"],
        "verification_status": "probable" if (direct_email or direct_phone) else "candidate",
        "missing_fields": missing_fields,
    }


def run_search(search_id: int) -> None:
    db = SessionLocal()
    try:
        search = db.get(Search, search_id)
        if search is None:
            return

        search.status = "running"
        search.started_at = utcnow()
        progress = {
            "companies_reviewed": 0,
            "pages_analyzed": 0,
            "pages_inaccessible": 0,
            "results_found": 0,
        }
        search.progress_json = dict(progress)
        db.commit()

        criteria = SearchCriteria.model_validate(search.criteria_json)
        results_saved = 0

        with httpx.Client() as http_client:
            discovery = discover_companies(criteria, max_companies=8)

            for company in discovery.companies:
                if results_saved >= search.max_results:
                    break

                db.refresh(search)
                if search.status == "cancelled":
                    return

                if not is_url_reachable(company.homepage_url, http_client):
                    progress["pages_inaccessible"] += 1
                    search.progress_json = dict(progress)
                    db.commit()
                    continue

                progress["companies_reviewed"] += 1

                homepage_html, error = fetch(company.homepage_url, http_client)
                if error:
                    progress["pages_inaccessible"] += 1
                    search.progress_json = dict(progress)
                    db.commit()
                    continue

                candidate_pages = [company.homepage_url]
                candidate_pages += discover_candidate_links(company.homepage_url, homepage_html, INVESTOR_KEYWORDS, limit=2)
                candidate_pages += discover_candidate_links(company.homepage_url, homepage_html, CANDIDATE_KEYWORDS, limit=2)

                for page_url in dict.fromkeys(candidate_pages):  # dedup preservando orden
                    if results_saved >= search.max_results:
                        break

                    if page_url == company.homepage_url:
                        page_html = homepage_html
                    else:
                        page_html, page_error = fetch(page_url, http_client)
                        if page_error:
                            progress["pages_inaccessible"] += 1
                            search.progress_json = dict(progress)
                            db.commit()
                            continue

                    extraction = extract_page(page_url, page_html)
                    progress["pages_analyzed"] += 1
                    search.progress_json = dict(progress)
                    db.commit()

                    for person in extraction["people_found"]:
                        if not person.get("job_title", "").strip():
                            continue  # nombre sin cargo explicito: no cumple "nombre Y cargo"
                        result_data = _build_result_data(
                            person, company.name, page_url, criteria,
                            extraction["emails_found"], extraction["phones_found"],
                        )
                        db.add(SearchResult(
                            search_id=search.id,
                            result_data_json=result_data,
                            status=result_data["verification_status"],
                            review_status="pending",
                        ))
                        results_saved += 1
                        progress["results_found"] = results_saved

                    search.progress_json = dict(progress)
                    db.commit()

        search.status = "completed"
        search.completed_at = utcnow()
        db.commit()
    except Exception as exc:  # noqa: BLE001 - se registra el error, no se relanza (BackgroundTask)
        search.status = "failed"
        search.error_message = str(exc)
        db.commit()
    finally:
        db.close()
