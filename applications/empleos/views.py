from datetime import timedelta

from django.db.models import DateField, Q
from django.db.models.functions import Cast
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views import View
from django.views.generic import ListView, TemplateView

from .forms import BusquedaForm
from .models import OfertaEmpleo
from .services import buscar_ofertas, guardar_ofertas


PERIODO_MAP = {
    "hoy": 0,
    "ayer": 1,
    "3d": 3,
    "1s": 7,
    "1m": 30,
}

CAMPOS_BUSQUEDA = ["title", "company", "location", "level", "source", "skills"]


def _aplicar_filtro_periodo(qs, periodo):
    dias = PERIODO_MAP.get(periodo)
    if dias is not None:
        fecha = timezone.localtime(timezone.now()).date() - timedelta(days=dias)
        qs = qs.annotate(
            posted_date_only=Cast('posted_date', DateField())
        ).filter(posted_date_only__gte=fecha)
    return qs


def _filtrar_keyword(qs, keyword):
    if not keyword:
        return qs
    filtro = Q()
    for palabra in keyword.split():
        for campo in CAMPOS_BUSQUEDA:
            filtro |= Q(**{f"{campo}__icontains": palabra})
    return qs.filter(filtro)


class BuscarEmpleoView(TemplateView):
    template_name = "empleos/buscar_empleo.html"


class BaseListaOfertasView(ListView):
    model = OfertaEmpleo
    paginate_by = 20
    context_object_name = "ofertas"
    oculto = False

    def get_queryset(self):
        keyword = self.request.GET.get("keyword", "").strip()
        fuente = self.request.GET.get("fuente", "").strip()
        periodo = self.request.GET.get("periodo", "").strip()

        qs = OfertaEmpleo.objects.filter(oculto=self.oculto).order_by('-posted_date')
        qs = _filtrar_keyword(qs, keyword)
        if fuente:
            qs = qs.filter(source=fuente)
        qs = _aplicar_filtro_periodo(qs, periodo)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["keyword"] = self.request.GET.get("keyword", "").strip()
        contexto = self._contexto_extra()
        context.update(contexto)
        context["total"] = self.get_queryset().count()
        return context

    def _contexto_extra(self):
        fuente = self.request.GET.get("fuente", "").strip()
        periodo = self.request.GET.get("periodo", "").strip()
        fuentes = OfertaEmpleo.objects.filter(oculto=self.oculto).values_list(
            "source", flat=True
        ).distinct().order_by("source")
        return {
            "fuentes": [f for f in fuentes if f],
            "fuente_seleccionada": fuente,
            "periodo": periodo,
        }


class EmpleosGuardadosView(BaseListaOfertasView):
    template_name = "empleos/empleos_guardados.html"
    oculto = False


class OfertasOcultasView(BaseListaOfertasView):
    template_name = "empleos/ofertas_ocultas.html"
    oculto = True


class ResultadosEmpleosView(View):
    def get(self, request):
        return render(request, "empleos/resultados_empleos.html",
                      {"error": "Usa el formulario para buscar."})

    def post(self, request):
        form = BusquedaForm(request.POST)
        if not form.is_valid():
            return render(request, "empleos/resultados_empleos.html",
                          {"error": "Revisa los datos del formulario."})

        data = form.cleaned_data
        filtros = {}
        for campo in ("search", "country_id", "from_age", "job_seniority"):
            if data.get(campo):
                filtros[campo] = data[campo]

        try:
            ofertas_api = buscar_ofertas(
                filtros=filtros,
                max_pages=data.get("max_pages") or 3,
            )
        except (ConnectionError, ValueError, RuntimeError) as e:
            return render(request, "empleos/resultados_empleos.html",
                          {"error": str(e)})
        except Exception as e:
            return render(request, "empleos/resultados_empleos.html",
                          {"error": f"Error inesperado: {e}"})

        nuevas, existentes, _ = guardar_ofertas(ofertas_api)
        return render(request, "empleos/buscar_empleo.html", {
            "total_resultados": len(ofertas_api),
            "nuevas": nuevas,
            "existentes": existentes,
        })


class ToggleOcultoView(View):
    def post(self, request, pk):
        oferta = get_object_or_404(OfertaEmpleo, pk=pk)
        oferta.oculto = not oferta.oculto
        oferta.save(update_fields=["oculto"])
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"oculto": oferta.oculto})
        referer = request.META.get("HTTP_REFERER", "")
        if "ocultas" in referer:
            return redirect("empleos_app:ofertas-ocultas")
        return redirect("empleos_app:empleos-guardados")


class EliminarOfertasAntiguasView(View):
    def post(self, request):
        limite = timezone.now() - timedelta(days=30)
        qs = OfertaEmpleo.objects.filter(posted_date__lt=limite)
        eliminadas = qs.count()
        qs.delete()
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"eliminadas": eliminadas})
        return redirect("empleos_app:ofertas-ocultas")
