from django.urls import path

from . import views

app_name = 'notificaciones_app'

urlpatterns = [
    path('notificaciones/', views.NotificacionesListView.as_view(), name='lista'),
    path('notificaciones/marcar-leidas/', views.MarcarLeidasView.as_view(), name='marcar-leidas'),
]