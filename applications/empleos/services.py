import base64
import os
import re
import time
from datetime import datetime
from zoneinfo import ZoneInfo

import requests
from django.conf import settings
from django.core.mail import EmailMultiAlternatives

from .models import OfertaEmpleo

API_URL = os.environ.get("CVM_API_URL", "https://api.getinjob.app/")
EMAIL = os.environ.get("CVM_EMAIL", "")
PASSWORD = os.environ.get("CVM_PASSWORD", "")
CLIENT_KEY = os.environ.get("CVM_CLIENT_KEY", "UnN3YUFWNHRpZzY5bEhzenV1YjRQQzRnTkpVdTF0")
CLIENT_VERSION = os.environ.get("CVM_CLIENT_VERSION", "1.0.0")
PLATFORM = os.environ.get("CVM_PLATFORM", "cvmatcher")
PAGE_SIZE = 25
TIMEOUT = 30
MAX_RETRIES = 3
RETRY_WAIT = 2

BROWSER_HEADERS = {
    "Origin": "https://dashboard.cvmatcher.app",
    "Referer": "https://dashboard.cvmatcher.app/",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
    ),
}

SOURCE_NAMES = {
    "computrabajo": "Computrabajo",
    "indeed": "Indeed",
    "linkedin": "LinkedIn",
    "bumeran": "Bumeran",
    "workdayjobs": "Workday",
    "myworkdayjobs": "Workday",
    "yondur": "Yondur",
    "supersol": "SuperSol",
    "coppel": "Coppel",
    "jobs": "Portal de empleo",
}

LEVELS = [
    (1, "Prácticas", re.compile(r"\bpracticante\b|\btrainee\b|\bpasante\b|\bbecario\b|\bpre[- ]?profesional\b", re.I)),
    (2, "Junior", re.compile(r"\bj[úu]nior\b|\bjr\.?\b|\bjun\.\b", re.I)),
    (3, "Semi Senior", re.compile(r"\bsemi[- ]?(?:senior|s?r)\.?\b|\bssr\.?\b", re.I)),
    (4, "Senior", re.compile(r"\bsenior\b|\bsr\.?\b|\bstaff\b|\blead\b|\bprincipal\b|\barchitect\b|\btech[- ]?lead\b|\bexperto\b", re.I)),
]


def _client_data_header() -> str:
    now = datetime.now(ZoneInfo("America/Lima"))
    formatted = f"{now.month}/{now.day}/{now.year}, {now.strftime('%I:%M:%S %p')}"
    return base64.b64encode(formatted.encode()).decode()


def _build_headers(token: str | None = None) -> dict:
    headers = {
        "x-client-data": _client_data_header(),
        "x-client-key": CLIENT_KEY,
        "x-client-version": CLIENT_VERSION,
        "x-platform": PLATFORM,
        "Content-Type": "application/json",
        **BROWSER_HEADERS,
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _detect_level(title: str) -> tuple:
    for rank, label, pattern in LEVELS:
        if pattern.search(title):
            return rank, label
    return 5, "Sin nivel"


def _source_from_url(url: str) -> str:
    try:
        domain = url.split("//", 1)[1].split("/", 1)[0].lower()
    except IndexError:
        return url
    for key, name in SOURCE_NAMES.items():
        if key in domain:
            return name
    parts = domain.replace("www.", "").split(".")
    return parts[0].capitalize() if parts else domain


def login() -> tuple:
    if not EMAIL or not PASSWORD:
        raise ValueError("Falta CVM_EMAIL o CVM_PASSWORD en el archivo .env")
    session = requests.Session()
    resp = session.post(
        f"{API_URL}auth/login/",
        json={"email": EMAIL, "password": PASSWORD},
        headers=_build_headers(),
        timeout=30,
    )
    if resp.status_code != 200:
        raise ConnectionError(f"Login fallido ({resp.status_code}): {resp.text[:300]}")
    data = resp.json()
    token = data.get("token")
    if not token:
        raise ConnectionError("Login exitoso pero la API no devolvió token")
    return session, token


def _parse_keywords(value: str) -> list:
    return [k.strip() for k in value.split(",") if k.strip()]


def _to_int_list(v) -> list:
    if isinstance(v, (list, tuple)):
        return [int(x) for x in v]
    return [int(v)]


def build_filter_body(filtros: dict) -> dict:
    body = {}
    search = filtros.get("search")
    if search:
        body["job"] = list(search) if isinstance(search, (list, tuple)) else [search]
    if filtros.get("country_id"):
        body["country_id"] = int(filtros["country_id"])
    if filtros.get("from_age"):
        body["from_age"] = int(filtros["from_age"])
    if filtros.get("type_order"):
        body["type_order"] = int(filtros["type_order"])
    if filtros.get("job_seniority"):
        body["job_seniority"] = _to_int_list(filtros["job_seniority"])
    if filtros.get("work_modality_id"):
        body["work_modality_id"] = _to_int_list(filtros["work_modality_id"])
    if filtros.get("job_category_id"):
        body["job_category_id"] = _to_int_list(filtros["job_category_id"])
    if filtros.get("job_type_id"):
        body["job_type_id"] = _to_int_list(filtros["job_type_id"])
    if filtros.get("salary_min"):
        body["salary_min"] = int(filtros["salary_min"])
    if filtros.get("salary_max"):
        body["salary_max"] = int(filtros["salary_max"])
    if filtros.get("currency_type"):
        body["currency_type"] = filtros["currency_type"]
    if filtros.get("p_english_req") is not None:
        body["p_english_req"] = bool(filtros["p_english_req"])
    return body


def _post_jobs_page(session: requests.Session, token: str, page: int, body: dict) -> dict:
    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = session.post(
                f"{API_URL}jobs/search",
                params={"page": page, "size": PAGE_SIZE, "with_match": "true"},
                json=body,
                headers=_build_headers(token=token),
                timeout=TIMEOUT,
            )
            if resp.status_code in (200, 201):
                return resp.json()
            last_error = f"HTTP {resp.status_code}: {resp.text[:200]}"
        except requests.exceptions.RequestException as exc:
            last_error = f"{type(exc).__name__}: {exc}"
        if attempt < MAX_RETRIES:
            time.sleep(RETRY_WAIT)
    raise RuntimeError(f"Página {page} falló tras {MAX_RETRIES} intentos: {last_error}")


def _parse_posted_date(raw: str):
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


def _jobs_from_response(data: dict) -> list:
    jobs = []
    for job in data.get("data", []):
        url = job.get("url")
        if not url:
            continue
        api_id = str(job.get("id") or url)
        rank, label = _detect_level(job.get("title") or "")
        jobs.append({
            "api_id": api_id,
            "title": job.get("title") or "Sin título",
            "company": job.get("company") or "",
            "location": job.get("location") or "",
            "salary_min": job.get("salary_min"),
            "salary_max": job.get("salary_max"),
            "currency_type": job.get("currency_type") or "",
            "posted_date": _parse_posted_date(job.get("posted_date")),
            "source": _source_from_url(url),
            "logo_url": (
                job.get("company_logo")
                or job.get("logo_url")
                or job.get("logo")
                or job.get("company_image")
                or job.get("image")
                or ""
            ),
            "skills": job.get("technical_skills") or [],
            "level_rank": rank,
            "level": label,
            "url": url,
        })
    return jobs


def _buscar_con_sesion(session, token, filtros: dict, max_pages: int = 3) -> list:
    body = build_filter_body(filtros)
    all_jobs: dict[str, dict] = {}
    page = 1

    while page <= max_pages:
        try:
            data = _post_jobs_page(session, token, page, body)
        except RuntimeError:
            break
        page_jobs = _jobs_from_response(data)
        for job in page_jobs:
            all_jobs[job["url"]] = job
        total = data.get("count") or 0
        if len(page_jobs) < PAGE_SIZE or total == 0 or page * PAGE_SIZE >= total:
            break
        page += 1

    return list(all_jobs.values())


def buscar_ofertas(filtros: dict, max_pages: int = 3) -> list:
    session, token = login()
    return _buscar_con_sesion(session, token, filtros, max_pages)


def buscar_ofertas_automaticas(filtros: dict, max_pages: int = 3) -> list:
    session, token = login()
    todos: dict[str, dict] = {}
    keywords = filtros.get("search") or []
    if isinstance(keywords, str):
        keywords = [keywords]
    for keyword in keywords:
        sub = dict(filtros)
        sub["search"] = keyword
        for job in _buscar_con_sesion(session, token, sub, max_pages):
            todos[job["url"]] = job
    return list(todos.values())


def _clave_orden(resultado):
    fecha = resultado["obj"].posted_date
    return (not resultado["es_nueva"], -(fecha.timestamp() if fecha else float("-inf")))


def guardar_ofertas(ofertas_api: list) -> tuple:
    nuevas = 0
    existentes = 0
    resultados = []

    for o in ofertas_api:
        obj, created = OfertaEmpleo.objects.update_or_create(
            api_id=o["api_id"],
            defaults={
                "title": o["title"],
                "company": o["company"],
                "location": o["location"],
                "salary_min": o.get("salary_min"),
                "salary_max": o.get("salary_max"),
                "currency_type": o.get("currency_type", ""),
                "posted_date": o.get("posted_date", ""),
                "source": o.get("source", ""),
                "logo_url": o.get("logo_url", ""),
                "skills": o.get("skills", []),
                "level_rank": o.get("level_rank", 5),
                "level": o.get("level", "Sin nivel"),
                "url": o["url"],
            },
        )
        if created:
            nuevas += 1
        else:
            existentes += 1
        resultados.append({"obj": obj, "es_nueva": created})

    resultados.sort(key=_clave_orden)
    return nuevas, existentes, resultados


def _formatear_salario(o: dict) -> str:
    if o.get("salary_min") and o.get("salary_max"):
        return f" {o['salary_min']} - {o['salary_max']} {o.get('currency_type', '').upper()}".rstrip()
    if o.get("salary_min"):
        return f" desde {o['salary_min']} {o.get('currency_type', '').upper()}".rstrip()
    return ""


def _linea_oferta(o: dict) -> str:
    salario = _formatear_salario(o)
    linea = (
        f"\u2022 {o['title']}\n"
        f"   Empresa: {o.get('company') or 'N/A'}\n"
        f"   Ubicaci\u00f3n: {o.get('location') or 'N/A'}"
    )
    if salario:
        linea += f"\n   Salario: {salario}"
    if o.get("level"):
        linea += f"\n   Nivel: {o['level']}"
    if o.get("source"):
        linea += f"\n   Fuente: {o['source']}"
    linea += f"\n   {o['url']}"
    return linea


def _linea_oferta_objeto(obj) -> str:
    o = {
        "title": obj.title,
        "company": obj.company,
        "location": obj.location,
        "salary_min": obj.salary_min,
        "salary_max": obj.salary_max,
        "currency_type": obj.currency_type,
        "level": obj.level,
        "source": obj.source,
        "url": obj.url,
    }
    return _linea_oferta(o)


def _resumen_nuevas(resultados_nuevos: list) -> str:
    if not resultados_nuevos:
        return ""
    lineas = [_linea_oferta_objeto(r["obj"]) for r in resultados_nuevos]
    return "\n\n".join(lineas)


def _dividir_texto(texto: str, limite=4000) -> list:
    if len(texto) <= limite:
        return [texto]
    partes = []
    actual = ""
    for bloque in texto.split("\n\n"):
        candidato = f"{actual}\n\n{bloque}" if actual else bloque
        if len(candidato) > limite and not actual:
            actual = bloque
            continue
        if len(candidato) <= limite:
            actual = candidato
        else:
            partes.append(actual)
            actual = bloque
    if actual:
        partes.append(actual)
    return partes


def enviar_telegram(chat_id: str, texto: str) -> bool:
    bot_token = getattr(settings, "TELEGRAM_BOT_TOKEN", "")
    chat_id_default = getattr(settings, "TELEGRAM_CHAT_ID", "")
    if not bot_token:
        return False
    destino = chat_id or chat_id_default
    if not destino:
        return False
    try:
        todas_ok = True
        for fragmento in _dividir_texto(texto):
            resp = requests.post(
                f"https://api.telegram.org/bot{bot_token}/sendMessage",
                json={"chat_id": destino, "text": fragmento, "disable_web_page_preview": False},
                timeout=30,
            )
            if resp.status_code != 200:
                todas_ok = False
        return todas_ok
    except requests.exceptions.RequestException:
        return False


def enviar_email_ofertas(destino: str, asunto: str, cuerpo: str) -> bool:
    if not destino:
        destino = settings.DEFAULT_FROM_EMAIL
    try:
        msg = EmailMultiAlternatives(
            subject=asunto,
            body=cuerpo,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[destino],
        )
        msg.attach_alternative(_cuerpo_html(cuerpo), "text/html")
        msg.send(fail_silently=False)
        return True
    except Exception:
        return False


def _cuerpo_html(texto_plano: str) -> str:
    parrafos = "".join(
        f"<p style='white-space:pre-wrap'>{p}</p>" for p in texto_plano.split("\n\n") if p
    )
    return f"<html><body style='font-family:Segoe UI,Arial,sans-serif'>{parrafos}</body></html>"
