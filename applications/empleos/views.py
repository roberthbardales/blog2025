from datetime import timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from django.db import models
from django.db.models.functions import Cast
from django.db.models import DateField

from .models import OfertaEmpleo
from .services import buscar_ofertas


PERIODO_MAP = {
    "hoy": 0,
    "ayer": 1,
    "3d": 3,
    "1s": 7,
    "1m": 30,
}


def _aplicar_filtro_periodo(qs, periodo):
    dias = PERIODO_MAP.get(periodo)
    if dias is not None:
        fecha = timezone.localdate() - timedelta(days=dias)
        qs = qs.annotate(
            posted_date_only=Cast('posted_date', DateField())
        ).filter(posted_date_only__gte=fecha)
    return qs


def buscar_empleo(request):
    return render(request, "empleos/buscar_empleo.html")


def empleos_guardados(request):
    fuente = request.GET.get("fuente", "").strip()
    periodo = request.GET.get("periodo", "").strip()

    ofertas = OfertaEmpleo.objects.filter(oculto=False)
    if fuente:
        ofertas = ofertas.filter(source=fuente)
    ofertas = _aplicar_filtro_periodo(ofertas, periodo)

    fuentes = OfertaEmpleo.objects.values_list("source", flat=True).distinct().order_by("source")

    return render(request, "empleos/empleos_guardados.html", {
        "ofertas": ofertas,
        "total": ofertas.count(),
        "fuentes": [f for f in fuentes if f],
        "fuente_seleccionada": fuente,
        "periodo": periodo,
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
        return render(request, "empleos/resultados_empleos.html", {"error": f"Error inesperado: {e}"})

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

    return render(request, "empleos/resultados_empleos.html", {
        "resultados": resultados,
        "total": len(resultados),
        "nuevas": nuevas,
        "existentes": existentes,
        "search": search,
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
    keyword = request.GET.get("keyword", "").strip()
    fuente = request.GET.get("fuente", "").strip()
    periodo = request.GET.get("periodo", "").strip()

    ofertas = OfertaEmpleo.objects.filter(oculto=True)
    if keyword:
        ofertas = ofertas.filter(
            models.Q(title__icontains=keyword) | models.Q(company__icontains=keyword)
        )
    if fuente:
        ofertas = ofertas.filter(source=fuente)
    ofertas = _aplicar_filtro_periodo(ofertas, periodo)

    fuentes = ofertas.values_list("source", flat=True).distinct().order_by("source")

    return render(request, "empleos/ofertas_ocultas.html", {
        "ofertas": ofertas,
        "total": ofertas.count(),
        "keyword": keyword,
        "fuentes": [f for f in fuentes if f],
        "fuente_seleccionada": fuente,
        "periodo": periodo,
    })
