# App Empleos - Cambios Avanzados

## Archivos creados

### Backend (`applications/empleos/`)

| Archivo | Descripción |
|---|---|
| `__init__.py` | Inicialización de la app |
| `apps.py` | Configuración de la app (`applications.empleos`) |
| `models.py` | Modelo `OfertaEmpleo` (sin FK a User, url unique) |
| `services.py` | Lógica API CVMATCHER (login, filtros, búsqueda, niveles) |
| `forms.py` | `EmpleoBusquedaForm` con todos los filtros |
| `views.py` | `AdminRequiredMixin` + CBVs (ListView, DetailView, DeleteView, TemplateView) |
| `api.py` | Endpoint AJAX `api_buscar_empleos` (POST, retorna JSON) |
| `urls.py` | Rutas con formato similar a otras apps |
| `admin.py` | Registro en Django Admin |
| `migrations/0001_initial.py` | Migración del modelo |

### Templates (`templates/empleos/`)

| Template | Descripción |
|---|---|
| `lista_empleos.html` | Tabla de ofertas con búsqueda, paginación |
| `buscar_empleo.html` | Formulario con todos los filtros + AJAX async |
| `detalle_empleo.html` | Detalle completo de la oferta |
| `eliminar_empleo.html` | Confirmación de eliminación |

## Archivos modificados

| Archivo | Cambio |
|---|---|
| `blog/settings.py` | Agregada app `'applications.empleos'` a `LOCAL_APPS` |
| `blog/urls.py` | Agregado `re_path('empleos/', include('applications.empleos.urls'))` |
| `templates/includes/barra_lateral.html` | Link "Empleos" visible para staff/superuser |
| `.env` | Variables `CVM_*` agregadas |

## URLs

| URL | Vista | Método |
|---|---|---|
| `empleos/` | `EmpleoListView` | GET |
| `empleos/buscar/` | `EmpleoBusquedaView` | GET |
| `empleos/api/buscar/` | `api_buscar_empleos` | POST (AJAX) |
| `empleos/<pk>/` | `EmpleoDetailView` | GET |
| `empleos/<pk>/eliminar/` | `EmpleoDeleteView` | POST |

## Variables de entorno (.env)

```
CVM_API_URL=https://api.getinjob.app/
CVM_EMAIL=tu_email
CVM_PASSWORD=tu_password
CVM_CLIENT_KEY=UnN3YUFWNHRpZzY5bEhzenV1YjRQQzRnTkpVdTF0
CVM_CLIENT_VERSION=1.0.0
CVM_PLATFORM=cvmatcher
```

## Funcionalidades

- Solo usuarios con `is_staff=True` o `is_superuser=True` pueden acceder
- Búsqueda AJAX async con redirección automática a la lista
- Tabla responsiva con columnas que se adaptan al tamaño de pantalla
- CRUD completo: listar, buscar, ver detalle, eliminar
- Upsert por URL (no duplica ofertas)
- Paginación (20 por página)
- Búsqueda por título en la lista

## Modelo OfertaEmpleo

```python
class OfertaEmpleo(TimeStampedModel):
    title = CharField(max_length=300)
    company = CharField(max_length=200, blank=True)
    location = CharField(max_length=200, blank=True)
    salary_min = IntegerField(null=True, blank=True)
    salary_max = IntegerField(null=True, blank=True)
    currency_type = CharField(max_length=10, blank=True)
    posted_date = CharField(max_length=50, blank=True)
    source = CharField(max_length=100, blank=True)
    logo_url = URLField(max_length=500, blank=True)
    skills = JSONField(default=list, blank=True)
    level_rank = IntegerField(default=5)
    level = CharField(max_length=30, blank=True)
    url = URLField(max_length=500, unique=True)
    keyword = CharField(max_length=100, blank=True)
```
