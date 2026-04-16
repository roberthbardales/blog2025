from django.urls import path
from . import views

app_name = 'amigos_app'

urlpatterns = [
    path('amigos/',           views.ListaAmigosView.as_view(),     name='lista'),
    path('amigos/buscar/',    views.BuscarUsuariosView.as_view(),  name='buscar'),
    path('amigos/enviar/<int:pk>/',   views.EnviarSolicitudView.as_view(),   name='enviar'),
    path('amigos/aceptar/<int:pk>/',  views.AceptarSolicitudView.as_view(),  name='aceptar'),
    path('amigos/rechazar/<int:pk>/', views.RechazarSolicitudView.as_view(), name='rechazar'),
    path('amigos/cancelar/<int:pk>/', views.CancelarSolicitudView.as_view(), name='cancelar'),
    path('amigos/eliminar/<int:pk>/', views.EliminarAmigoView.as_view(),     name='eliminar'),
    path('amigos/bloquear/<int:pk>/', views.BloquearUsuarioView.as_view(),   name='bloquear'),
    path('amigos/perfil/', views.PerfilRedView.as_view(), name='perfil'),
]