#
from django.urls import path
from . import views

app_name = "entrada_app"

urlpatterns = [

    # path(
    #     'entradas_general/',
    #     views.EntryListViewBySearch.as_view(),
    #     name='entry-lista-general',
    # ),
    path(
        'entradas/',
        views.EntryListView.as_view(),
        name='entry-lista',
    ),
    path(
        'entrada/<slug>/',
        views.EntryDetailView.as_view(),
        name='entry-detail',
    ),
    path(
        'agregar/',
        views.AgregarEntradaCreateView.as_view(),
        name='add-entrada',
    ),

    path(
        'actualizar/<pk>/',
        views.ActualizarEntradaUpdateView.as_view(),
        name='update-entrada',
    ),
    path(
        'entry/<slug:slug>/comment/',
        views.CommentCreateView.as_view(),
        name='add_comment',
    ),
    #like
        path(
        'entrada/<int:pk>/like/',
        views.ToggleLikeView.as_view(),
        name='toggle-like',
    ),
        path(
        'comment/<int:pk>/delete/',
        views.CommentDeleteView.as_view(),
        name='delete_comment'),

    #ver usuarios
    path(
        'users/<int:pk>/',
         views.UserProfileView.as_view(),
         name='view_profile'
    ),
]