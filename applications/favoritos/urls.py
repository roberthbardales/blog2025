#
from django.urls import path
from . import views

app_name = "favoritos_app"

urlpatterns = [
    path(
        'perfil',
        views.UserPageView.as_view(),
        name='perfil',
    ),
    path(
        'add-entrada/<pk>',
        views.AddFavoritosView.as_view(),
        name='add-favoritos',
    ),
    path(
        'delete-favorites/<pk>',
        views.FavoritesDeleteView.as_view(),
        name='delete-favoritos',
    ),

    #pruebas añadir favorito
    path(
        'add-entrada2/<pk>',
        views.AddFavoritosView2.as_view(),
        name='add-favoritos2',
    ),

    #fin prueba


    #añadir quitar
    path(
        'toggle-favorito/<int:pk>/',
         views.ToggleFavoritoView.as_view(),
         name='toggle-favorito'
    ),

    # CRUD de grupos
    path(
        "grupos_crud/",
        views.GruposCRUDView.as_view(),
        name="grupos_crud"
    ),
    path(
        "grupo_editar/<int:pk>",
        views.EditarGrupoView.as_view(),
        name="grupo_editar"),
    path(
        "favoritos_por_grupo/<int:pk>/",
        views.FavoritosByGrupoListView.as_view(),
        name="favoritos_por_grupo",
    ),
    path(
         "cambiar-grupo/<int:pk>/",
         views.CambiarGrupoView.as_view(),
         name='cambiar-grupo',
    ),

    #prueba
    # path(
    #     "prueba/",
    #     views.PruebaListView.as_view(),
    #     name="prueba",
    # ),
]
