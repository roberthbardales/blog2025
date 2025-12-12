#
from django.urls import path
from . import views

app_name = "notas_app"

urlpatterns = [

    # path(
    #     'entradas_general/',
    #     views.EntryListViewBySearch.as_view(),
    #     name='entry-lista-general',
    # ),
    path(
        'notas/',
        views.NotaListView.as_view(),
        name='lista-notas'
    ),
    path(
        'nota/<int:pk>/',
        views.NotaDetailView.as_view(),
        name='detalle-nota'
    ),
    path(
        'crear_nota/',
        views.NotaCreateView.as_view(),
        name='crear-nota'
    ),
    path(
        'editar_nota/<int:pk>/',
        views.NotaUpdateView.as_view(),
        name='editar-nota'
    ),
    path(
        'eliminar_nota/<int:pk>/',
        views.NotaDeleteView.as_view(),
        name='eliminar-nota'
    ),
]

