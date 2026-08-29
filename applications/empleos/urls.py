from django.urls import path
from . import views

app_name = "empleos_app"

urlpatterns = [
    path('empleos/buscar/',      views.buscar_empleo,      name='buscar-empleo'),
    path('empleos/guardados/',   views.empleos_guardados,   name='empleos-guardados'),
    path('empleos/ocultas/',     views.ofertas_ocultas,     name='ofertas-ocultas'),
    path('empleos/toggle/<int:pk>/', views.toggle_oculto,   name='toggle-oculto'),
    path('empleos/eliminar-antiguas/', views.eliminar_ofertas_antiguas, name='eliminar-antiguas'),
    path('empleos/resultados/',  views.resultados_empleos,  name='resultados-empleos'),
]
