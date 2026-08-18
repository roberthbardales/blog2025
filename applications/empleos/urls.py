from django.urls import path
from . import views

app_name = "empleos_app"

urlpatterns = [
    path('empleos/buscar/', views.buscar_empleo, name='buscar-empleo'),
    path('empleos/resultados/', views.resultados_empleos, name='resultados-empleos'),
    path('empleos/historial/', views.historial_empleos, name='historial-empleos'),
]
