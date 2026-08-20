from datetime import date, timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from django.core.paginator import Paginator
from django.db import models
from django.db.models import DateField
from django.db.models.functions import Cast

from .models import OfertaEmpleo
from .services import buscar_ofertas


PERIODO_MAP = {
    "hoy": 0,
    "ayer": 1,
    "3d": 3,
    "1s": 7,
    "1m": 30,
}

COUNTRY_NAMES = {
    "1": "Perú",
    "2": "México",
    "3": "Colombia",
    "4": "Chile",
    "5": "Argentina",
    "6": "España",
}

SENIORITY_NAMES = {
    "1": "Prácticas",
    "2": "Junior",
    "3": "Semi Senior",
    "4": "Senior",
}


def _aplicar_filtro_periodo(qs, periodo):
    dias = PERIODO_MAP.get(periodo)
    if dias is not None:
        fecha = date.today() - timedelta(days=dias)
        qs = qs.annotate(
            posted_date_only=Cast('posted_date', DateField())
        ).filter(posted_date_only__gte=fecha)
    return qs


def _filtrar_keyword(qs, keyword):
    if not keyword:
        return qs
    palabras = keyword.split()
    filtro = models.Q()
    for palabra in palabras:
        filtro |= (
            models.Q(title__icontains=palabra) |
            models.Q(company__icontains=palabra) |
            models.Q(location__icontains=palabra) |
            models.Q(level__icontains=palabra) |
            models.Q(source__icontains=palabra) |
            models.Q(skills__icontains=palabra)
        )
    return qs.filter(filtro)


def _filtrar_ofertas(request, oculto):
    keyword = request.GET.get("keyword", "").strip()
    fuente = request.GET.get("fuente", "").strip()
    periodo = request.GET.get("periodo", "").strip()
    page_number = request.GET.get("page", 1)

    ofertas = OfertaEmpleo.objects.filter(oculto=oculto).order_by('-posted_date')
    ofertas = _filtrar_keyword(ofertas, keyword)
    if fuente:
        ofertas = ofertas.filter(source=fuente)
    ofertas = _aplicar_filtro_periodo(ofertas, periodo)

    total = ofertas.count()
    paginator = Paginator(ofertas, 20)
    page_obj = paginator.get_page(page_number)

    fuentes = OfertaEmpleo.objects.filter(oculto=oculto).values_list(
        "source", flat=True
    ).distinct().order_by("source")

    return page_obj, {
        "total": total,
        "keyword": keyword,
        "fuentes": [f for f in fuentes if f],
        "fuente_seleccionada": fuente,
        "periodo": periodo,
    }


def buscar_empleo(request):
    return render(request, "empleos/buscar_empleo.html")


def empleos_guardados(request):
    page_obj, contexto = _filtrar_ofertas(request, oculto=False)
    return render(request, "empleos/empleos_guardados.html", {
        "ofertas": page_obj,
        "page_obj": page_obj,
        **contexto,
    })


def resultados_empleos(request):
    if request.method != "POST":
        return render(request, "empleos/resultados_empleos.html", {"error": "Usa el formulario para buscar."})

    search = request.POST.get("search", "").strip()
    country_id = request.POST.get("country_id", "")
    from_age = request.POST.get("from_age", "")
    max_pages = request.POST.get("max_pages", "3")
    job_seniority = request.POST.getlist("job_seniority")

    filtros = {}
    if search:
        filtros["search"] = search
    if country_id:
        filtros["country_id"] = country_id
    if from_age:
        filtros["from_age"] = from_age
    if job_seniority:
        filtros["job_seniority"] = job_seniority

    try:
        ofertas_api = buscar_ofertas(
            filtros=filtros,
            max_pages=min(int(max_pages), 10),
        )
    except (ConnectionError, ValueError, RuntimeError) as e:
        return render(request, "empleos/resultados_empleos.html", {"error": str(e)})
    except Exception as e:
        return render(request, "empleos/resultados_empleos.html",
                      {"error": f"Error inesperado: {e}"})

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
            resultados.append({"obj": obj, "es_nueva": True})
        else:
            existentes += 1
            resultados.append({"obj": obj, "es_nueva": False})

    def _clave_orden(r):
        fecha = r["obj"].posted_date
        return (not r["es_nueva"], -(fecha.timestamp() if fecha else float("-inf")))

    resultados.sort(key=_clave_orden)

    return render(request, "empleos/resultados_empleos.html", {
        "resultados": resultados,
        "total": len(resultados),
        "nuevas": nuevas,
        "existentes": existentes,
        "search": search,
        "country": COUNTRY_NAMES.get(country_id, ""),
        "niveles": [SENIORITY_NAMES.get(s, s) for s in job_seniority],
    })


def toggle_oculto(request, pk):
    if request.method != "POST":
        return redirect("empleos_app:empleos-guardados")
    oferta = get_object_or_404(OfertaEmpleo, pk=pk)
    oferta.oculto = not oferta.oculto
    oferta.save(update_fields=["oculto"])
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"oculto": oferta.oculto})
    referer = request.META.get("HTTP_REFERER", "")
    if "ocultas" in referer:
        return redirect("empleos_app:ofertas-ocultas")
    return redirect("empleos_app:empleos-guardados")


def ofertas_ocultas(request):
    page_obj, contexto = _filtrar_ofertas(request, oculto=True)
    return render(request, "empleos/ofertas_ocultas.html", {
        "ofertas": page_obj,
        "page_obj": page_obj,
        **contexto,
    })
