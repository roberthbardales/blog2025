# Plan: App `evaluaciones` (Cuestionarios)

Módulo de evaluaciones por temas: se crea un tema (ej. "django"), se le agregan preguntas con 4 opciones, y al resolverlo se muestra cuántas respuestas fueron correctas e incorrectas.

## Decisiones

- **Permisos**: todos pueden todo (cualquier usuario logueado crea temas/preguntas y resuelve).
- **Formato**: una pregunta a la vez con JS (botones siguiente/anterior + barra de progreso).
- **Historial**: no se guardan resultados, solo se muestran al final.
- **Aleatoriedad**: preguntas y opciones se mezclan en cada intento.

## Estructura

```
applications/evaluaciones/
├── __init__.py
├── apps.py
├── admin.py
├── forms.py
├── models.py
├── urls.py
└── views.py

templates/evaluaciones/
├── base_evaluaciones.html
├── tema_list.html
├── tema_form.html
├── tema_confirm_delete.html
├── pregunta_list.html
├── pregunta_form.html
└── evaluacion.html
```

## Modelos (`applications/evaluaciones/models.py`)

Estilo del proyecto: heredar de `TimeStampedModel` (model_utils), Meta con `verbose_name`, slug autogenerado en `save()` (como `Entry`).

```python
class Tema(TimeStampedModel):
    nombre = models.CharField('Nombre', max_length=100, unique=True)
    descripcion = models.TextField('Descripción', blank=True)
    slug = models.SlugField(editable=False, max_length=120, unique=True)

class Pregunta(TimeStampedModel):
    tema = models.ForeignKey(Tema, on_delete=models.CASCADE, related_name='preguntas')
    texto = models.TextField('Pregunta')
    explicacion = models.TextField('Explicación', blank=True)

class Opcion(TimeStampedModel):
    pregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE, related_name='opciones')
    texto = models.TextField('Opción')
    es_correcta = models.BooleanField(default=False)
```

## Vistas (`applications/evaluaciones/views.py`)

CBVs con `LoginRequiredMixin` (todos pueden todo):

**Temas**
- `TemaListView` — lista de temas disponibles
- `TemaCreateView` / `TemaUpdateView` / `TemaDeleteView`

**Preguntas**
- `PreguntaListView` — preguntas de un tema
- `PreguntaCreateView` / `PreguntaUpdateView` — formulario con `inlineformset_factory(Pregunta, Opcion, extra=4)` para las 4 opciones en un solo form
- `PreguntaDeleteView`

**Resolver evaluación**
- `EvaluacionView` — renderiza el quiz del tema:
  - Preguntas mezcladas: `.order_by('?')`
  - Opciones barajadas en Python al armar el contexto
  - JS muestra una pregunta por vez; las correctas NO van visibles en el HTML
- `CalificarEvaluacionView` — endpoint POST AJAX:
  - Recibe `{pregunta_id: opcion_elegida_id, ...}`
  - Corrige contra `es_correcta` en servidor
  - Devuelve JSON `{correctas, incorrectas, total, detalle: [{pregunta_id, opcion_correcta_id, elegida_id}]}`
  - JS pinta la pantalla final con aciertos/fallos y detalle de errores

## URLs

`applications/evaluaciones/urls.py` con `app_name = 'evaluaciones'`:

```python
urlpatterns = [
    path('', TemaListView.as_view(), name='tema-lista'),
    path('tema/agregar/', TemaCreateView.as_view(), name='tema-agregar'),
    path('tema/editar/<slug:slug>/', TemaUpdateView.as_view(), name='tema-editar'),
    path('tema/eliminar/<slug:slug>/', TemaDeleteView.as_view(), name='tema-eliminar'),
    path('tema/<slug:slug>/preguntas/', PreguntaListView.as_view(), name='pregunta-lista'),
    path('tema/<slug:slug>/pregunta/agregar/', PreguntaCreateView.as_view(), name='pregunta-agregar'),
    path('pregunta/editar/<int:pk>/', PreguntaUpdateView.as_view(), name='pregunta-editar'),
    path('pregunta/eliminar/<int:pk>/', PreguntaDeleteView.as_view(), name='pregunta-eliminar'),
    path('tema/<slug:slug>/resolver/', EvaluacionView.as_view(), name='evaluacion'),
    path('tema/<slug:slug>/calificar/', CalificarEvaluacionView.as_view(), name='calificar'),
]
```

Montar en `blog/urls.py`:

```python
path('evaluaciones/', include('applications.evaluaciones.urls')),
```

## Registro

1. Agregar `'applications.evaluaciones'` a `LOCAL_APPS` en `blog/settings.py`.
2. `python manage.py makemigrations evaluaciones && python manage.py migrate`.

## Admin (`applications/evaluaciones/admin.py`)

Registrar modelos con inlines para cargar preguntas rápido desde `/admin/`:

```python
class OpcionInline(admin.TabularInline):
    model = Opcion
    extra = 4

@admin.register(Pregunta)
class PreguntaAdmin(admin.ModelAdmin):
    inlines = [OpcionInline]
    list_filter = ['tema']

admin.site.register(Tema)
```

## Templates

En `templates/evaluaciones/`, extendiendo de `base.html` vía `base_evaluaciones.html`:

- `tema_list.html` — tarjetas de temas con nº de preguntas y botón "Resolver"
- `tema_form.html` / `tema_confirm_delete.html`
- `pregunta_list.html` — preguntas del tema con sus opciones (marca la correcta)
- `pregunta_form.html` — pregunta + formset de 4 opciones (checkbox/radio de correcta)
- `evaluacion.html` — quiz: contenedor de preguntas ocultas, navegación JS una-por-una, barra de progreso, fetch POST a calificar con CSRF token, pantalla de resultados

## Pendiente / ideas futuras

- Límite de tiempo por evaluación
- Importar preguntas masivamente desde JSON/CSV (management command)
- Historial de intentos y mejor puntaje por usuario
