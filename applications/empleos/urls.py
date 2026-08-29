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
]
