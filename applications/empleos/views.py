from django.shortcuts import render
from .models import OfertaEmpleo, Busqueda
from .services import buscar_ofertas


def buscar_empleo(request):
    return render(request, "empleos/buscar_empleo.html")


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

    busqueda = Busqueda.objects.create(
        keyword=search or "(sin palabra clave)",
        total_encontradas=len(ofertas_api),
    )

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
        busqueda.ofertas.add(obj)
        if created:
            nuevas += 1
            resultados.append({"obj": obj, "es_nueva": True})
        else:
            existentes += 1
            resultados.append({"obj": obj, "es_nueva": False})

    busqueda.nuevas = nuevas
    busqueda.existentes = existentes
    busqueda.save(update_fields=["nuevas", "existentes"])

    return render(request, "empleos/resultados_empleos.html", {
        "resultados": resultados,
        "total": len(resultados),
        "nuevas": nuevas,
        "existentes": existentes,
        "search": search,
    })


def historial_empleos(request):
    keyword = request.GET.get("keyword", "").strip()
    ofertas = OfertaEmpleo.objects.all()
    if keyword:
        ofertas = ofertas.filter(busquedas__keyword__icontains=keyword)
    busquedas = Busqueda.objects.all()
    return render(request, "empleos/historial_empleos.html", {
        "ofertas": ofertas,
        "total": ofertas.count(),
        "busquedas": busquedas,
        "keyword": keyword,
    })
