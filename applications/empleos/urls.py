from django.urls import path
from . import views

app_name = "empleos_app"

urlpatterns = [
    path('empleos/buscar/',   views.BuscarEmpleoView.as_view(),        name='buscar-empleo'),
    path('empleos/guardados/', views.EmpleosGuardadosView.as_view(),   name='empleos-guardados'),
    path('empleos/ocultas/',  views.OfertasOcultasView.as_view(),      name='ofertas-ocultas'),
    path('empleos/toggle/<int:pk>/', views.ToggleOcultoView.as_view(), name='toggle-oculto'),
    path('empleos/eliminar-antiguas/', views.EliminarOfertasAntiguasView.as_view(), name='eliminar-antiguas'),
    path('empleos/resultados/', views.ResultadosEmpleosView.as_view(), name='resultados-empleos'),
    path('empleos/filtros/', views.FiltroEmpleoListView.as_view(), name='filtros-lista'),
    path('empleos/filtros/nuevo/', views.FiltroEmpleoCreateView.as_view(), name='filtro-nuevo'),
    path('empleos/filtros/<int:pk>/editar/', views.FiltroEmpleoUpdateView.as_view(), name='filtro-editar'),
    path('empleos/filtros/<int:pk>/eliminar/', views.FiltroEmpleoDeleteView.as_view(), name='filtro-eliminar'),
    path('empleos/filtros/<int:pk>/toggle/', views.FiltroEmpleoToggleView.as_view(), name='filtro-toggle'),
]
