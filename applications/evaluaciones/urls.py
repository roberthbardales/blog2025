from django.urls import path

from . import views

app_name = 'evaluaciones_app'

urlpatterns = [
    path(
        'evaluaciones/',
        views.TemaListView.as_view(),
        name='tema-lista'
    ),
    path(
        'evaluaciones/tema/agregar/',
        views.TemaCreateView.as_view(),
        name='tema-agregar'
    ),
    path(
        'evaluaciones/tema/editar/<slug:slug>/',
        views.TemaUpdateView.as_view(),
        name='tema-editar'
    ),
    path(
        'evaluaciones/tema/eliminar/<slug:slug>/',
        views.TemaDeleteView.as_view(),
        name='tema-eliminar'
    ),
    path(
        'evaluaciones/tema/<slug:slug>/preguntas/',
        views.PreguntaListView.as_view(),
        name='pregunta-lista'
    ),
    path(
        'evaluaciones/tema/<slug:slug>/pregunta/agregar/',
        views.PreguntaCreateView.as_view(),
        name='pregunta-agregar'
    ),
    path(
        'evaluaciones/pregunta/editar/<int:pk>/',
        views.PreguntaUpdateView.as_view(),
        name='pregunta-editar'
    ),
    path(
        'evaluaciones/pregunta/eliminar/<int:pk>/',
        views.PreguntaDeleteView.as_view(),
        name='pregunta-eliminar'
    ),
    path(
        'evaluaciones/tema/<slug:slug>/importar-json/',
        views.ImportarJSONView.as_view(),
        name='importar-json'
    ),
    path(
        'evaluaciones/tema/<slug:slug>/resolver/configurar/',
        views.ConfigurarEvaluacionView.as_view(),
        name='configurar-evaluacion'
    ),
    path(
        'evaluaciones/tema/<slug:slug>/resolver/',
        views.EvaluacionView.as_view(),
        name='evaluacion'
    ),
    path(
        'evaluaciones/pregunta/<int:pk>/verificar/',
        views.VerificarPreguntaView.as_view(),
        name='verificar-pregunta'
    ),
    path(
        'evaluaciones/tema/<slug:slug>/calificar/',
        views.CalificarEvaluacionView.as_view(),
        name='calificar'
    ),
]
