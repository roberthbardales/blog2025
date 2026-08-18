import argparse
import base64
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import requests
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

API_URL = os.getenv("CVM_API_URL", "https://api.getinjob.app/")
EMAIL = os.getenv("CVM_EMAIL")
PASSWORD = os.getenv("CVM_PASSWORD")
CLIENT_KEY = os.getenv("CVM_CLIENT_KEY", "UnN3YUFWNHRpZzY5bEhzenV1YjRQQzRnTkpVdTF0")
CLIENT_VERSION = os.getenv("CVM_CLIENT_VERSION", "1.0.0")
PLATFORM = os.getenv("CVM_PLATFORM", "cvmatcher")

RESULTS_FILE = BASE_DIR / "ofertas.json"
FILTERS_FILE = BASE_DIR / "filtros.json"
PAGE_SIZE = 25
TIMEOUT = 70
MAX_RETRIES = 6
RETRY_WAIT = 2

BROWSER_HEADERS = {
    "Origin": "https://dashboard.cvmatcher.app",
    "Referer": "https://dashboard.cvmatcher.app/",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
    ),
}

TIME_FILTERS = {
    "1": 1,
    "3": 3,
    "7": 7,
    "14": 14,
    "30": 30,
}

DEFAULT_FILTERS = {
    "search": ["python", "hacking", "django"],
    "country_id": 1,
    "from_age": 3,
    "type_order": 1,
    "job_category_id": [3],
    "job_seniority": [2, 1, 4],
}


def client_data_header():
    now = datetime.now(ZoneInfo("America/Lima"))
    formatted = f"{now.month}/{now.day}/{now.year}, {now.strftime('%I:%M:%S %p')}"
    return base64.b64encode(formatted.encode()).decode()


def build_headers(token=None, extra=None):
    headers = {
        "x-client-data": client_data_header(),
        "x-client-key": CLIENT_KEY,
        "x-client-version": CLIENT_VERSION,
        "x-platform": PLATFORM,
        "Content-Type": "application/json",
        **BROWSER_HEADERS,
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if extra:
        headers.update(extra)
    return headers


def login(session):
    if not EMAIL or not PASSWORD:
        sys.exit("Falta CVM_EMAIL o CVM_PASSWORD en el archivo .env")
    resp = session.post(
        f"{API_URL}auth/login/",
        json={"email": EMAIL, "password": PASSWORD},
        headers=build_headers(),
        timeout=30,
    )
    if resp.status_code != 200:
        sys.exit(
            f"Login fallido ({resp.status_code}). Respuesta:\n{resp.text[:500]}"
        )
    data = resp.json()
    token = data.get("token")
    if token:
        session.cookies.set("token", token, path="/")
    return data, token


def load_filters():
    if FILTERS_FILE.exists():
        try:
            loaded = json.loads(FILTERS_FILE.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                merged = DEFAULT_FILTERS.copy()
                merged.update(loaded)
                return merged
            return DEFAULT_FILTERS.copy()
        except (ValueError, OSError):
            return DEFAULT_FILTERS.copy()
    return DEFAULT_FILTERS.copy()


def build_filter_body(filters, keyword=None):
    body = {}
    if keyword is not None:
        body["job"] = [keyword]
    elif filters.get("search"):
        body["job"] = filters["search"] if isinstance(filters["search"], list) else [filters["search"]]
    if filters.get("location"):
        body["location"] = filters["location"]
    if filters.get("country_id"):
        body["country_id"] = int(filters["country_id"])
    if filters.get("from_age"):
        body["from_age"] = int(filters["from_age"])
    if filters.get("type_order"):
        body["type_order"] = int(filters["type_order"])
    if filters.get("job_category_id"):
        body["job_category_id"] = [int(x) for x in filters["job_category_id"]]
    if filters.get("job_seniority"):
        body["job_seniority"] = [int(x) for x in filters["job_seniority"]]
    if filters.get("work_modality_id"):
        body["work_modality_id"] = [int(x) for x in filters["work_modality_id"]]
    if filters.get("job_type_id"):
        body["job_type_id"] = [int(x) for x in filters["job_type_id"]]
    if filters.get("salary_min"):
        body["salary_min"] = int(filters["salary_min"])
    if filters.get("salary_max"):
        body["salary_max"] = int(filters["salary_max"])
    if filters.get("currency_type"):
        body["currency_type"] = filters["currency_type"]
    if filters.get("p_english_req") is not None:
        body["p_english_req"] = bool(filters["p_english_req"])
    return body


def post_jobs_page(session, token, page, body):
    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = session.post(
                f"{API_URL}jobs/search",
                params={"page": page, "size": PAGE_SIZE, "with_match": "true"},
                json=body,
                headers=build_headers(token=token),
                timeout=TIMEOUT,
            )
            if resp.status_code in (200, 201):
                try:
                    return resp.json()
                except ValueError:
                    last_error = f"respuesta no JSON: {resp.text[:200]}"
            else:
                last_error = f"HTTP {resp.status_code}: {resp.text[:150]}"
        except requests.exceptions.RequestException as exc:
            last_error = f"{type(exc).__name__}: {exc}"
        if attempt < MAX_RETRIES:
            print(f"    pagina {page}: intento {attempt}/{MAX_RETRIES} -> {last_error}")
            time.sleep(RETRY_WAIT)
    raise RuntimeError(f"pagina {page} fallo tras {MAX_RETRIES} intentos: {last_error}")


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
    (1, "Practicas", re.compile(r"\bpracticante\b|\btrainee\b|\bpasante\b|\bbecario\b|\bpre[- ]?profesional\b", re.I)),
    (2, "Junior", re.compile(r"\bj[Ãºu]nior\b|\bjr\.?\b|\bjun\.\b", re.I)),
    (3, "Semi Senior", re.compile(r"\bsemi[- ]?(?:senior|s?r)\.?\b|\bssr\.?\b", re.I)),
    (4, "Senior", re.compile(r"\bsenior\b|\bsr\.?\b|\bstaff\b|\blead\b|\bprincipal\b|\barchitect\b|\btech[- ]?lead\b|\bexperto\b", re.I)),
]


def detect_level(title):
    for rank, label, pattern in LEVELS:
        if pattern.search(title):
            return rank, label
    return 5, "Sin nivel"


def source_from_url(url):
    try:
        domain = url.split("//", 1)[1].split("/", 1)[0].lower()
    except IndexError:
        return url
    for key, name in SOURCE_NAMES.items():
        if key in domain:
            return name
    parts = domain.replace("www.", "").split(".")
    return parts[0].capitalize() if parts else domain


def jobs_from_response(data):
    jobs = []
    for job in data.get("data", []):
        url = job.get("url")
        if not url:
            continue
        rank, label = detect_level(job.get("title") or "")
        jobs.append(
            {
                "title": job.get("title") or "Sin titulo",
                "company": job.get("company") or "",
                "location": job.get("location") or "",
                "salary_min": job.get("salary_min"),
                "salary_max": job.get("salary_max"),
                "currency_type": job.get("currency_type") or "",
                "posted_date": job.get("posted_date") or "",
                "source": source_from_url(url),
                "logo_url": (
                    job.get("company_logo")
                    or job.get("logo_url")
                    or job.get("logo")
                    or job.get("company_image")
                    or job.get("image")
                    or ""
                ),
                "skills": (job.get("technical_skills") or [])[:8],
                "level_rank": rank,
                "level": label,
                "url": url,
            }
        )
    return jobs


def fetch_jobs(session, token, body, max_pages):
    jobs = {}
    page = 1
    while page <= max_pages:
        try:
            data = post_jobs_page(session, token, page, body)
        except RuntimeError as exc:
            print(f"  Abortando: {exc}")
            break
        page_jobs = jobs_from_response(data)
        before = len(jobs)
        for job in page_jobs:
            jobs[job["url"]] = job
        total = data.get("count") or 0
        print(
            f"  Pagina {page}: {len(jobs) - before} ofertas nuevas "
            f"({total} en total)"
        )
        if len(page_jobs) < PAGE_SIZE or total == 0 or page * PAGE_SIZE >= total:
            break
        page += 1
    return list(jobs.values())


def save_results(searches, filters):
    generated = datetime.now(ZoneInfo("America/Lima")).strftime(
        "%d/%m/%Y %H:%M:%S"
    )
    payload = {
        "generated": generated,
        "filters": filters,
        "searches": searches,
    }
    RESULTS_FILE.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def main():
    parser = argparse.ArgumentParser(description="Scraper de ofertas CVMATCHER")
    parser.add_argument("--search", nargs="*", help="Palabras clave (ej: python)")
    parser.add_argument("--country", type=int, help="country_id (1 = Peru)")
    parser.add_argument("--days", type=int, help="Dias: 1, 3, 7, 14, 30 (from_age)")
    parser.add_argument("--order", type=int, help="type_order (1 = relevancia)")
    parser.add_argument("--location", help="Ubicacion (ej: Lima)")
    parser.add_argument("--modality", type=int, action="append", help="work_modality_id")
    parser.add_argument("--seniority", type=int, action="append", help="job_seniority")
    parser.add_argument("--job-type", type=int, action="append", help="job_type_id")
    parser.add_argument("--salary-min", type=int)
    parser.add_argument("--salary-max", type=int)
    parser.add_argument("--english", action="store_true", help="p_english_req=true")
    parser.add_argument(
        "--max-pages",
        type=int,
        default=2000,
        help="Maximo de paginas a recorrer (default 2000)",
    )
    args = parser.parse_args()

    filters = load_filters()
    if args.search:
        filters["search"] = args.search
    if args.country is not None:
        filters["country_id"] = args.country
    if args.days is not None:
        filters["from_age"] = args.days
    if args.order is not None:
        filters["type_order"] = args.order
    if args.location:
        filters["location"] = args.location
    if args.modality:
        filters["work_modality_id"] = args.modality
    if args.seniority:
        filters["job_seniority"] = args.seniority
    if args.job_type:
        filters["job_type_id"] = args.job_type
    if args.salary_min is not None:
        filters["salary_min"] = args.salary_min
    if args.salary_max is not None:
        filters["salary_max"] = args.salary_max
    if args.english:
        filters["p_english_req"] = True

    keywords = filters.get("search") or [""]
    print(f"Backend: {API_URL}")
    print(f"Busquedas: {keywords}")

    session = requests.Session()
    _, token = login(session)
    print("Login OK")

    searches = []
    for keyword in keywords:
        body = build_filter_body(filters, keyword)
        print(f"\nBuscando '{keyword}' ...")
        print(f"Filtros: {json.dumps(body, ensure_ascii=False)}")
        jobs = fetch_jobs(session, token, body, args.max_pages)
        searches.append(
            {
                "keyword": keyword,
                "jobs": jobs,
            }
        )
        print(f"Total '{keyword}': {len(jobs)} ofertas")

    save_results(searches, filters)
    print(f"\nGuardado: ofertas.json")


if __name__ == "__main__":
    main()
