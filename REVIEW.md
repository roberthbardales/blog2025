# Blog2025 — Resumen de avances

## App Empleos (18 ago 2026)

### Modelo
- Eliminado modelo `Busqueda` y M2M `busquedas` de `OfertaEmpleo` (migración `0006`)
- Campo `oculto = BooleanField(default=False)` agregado a `OfertaEmpleo` (migración `0005`)

### Vistas (`applications/empleos/views.py`)
- `empleos_guardados` — excluye ofertas con `oculto=True`; filtros por fuente y período (sin keyword)
- `ofertas_ocultas` — lista ofertas ocultas con filtros; permite restaurar
- `toggle_oculto` — endpoint POST que alterna estado oculto (soporta AJAX)
- `_aplicar_filtro_periodo` — helper que mapea período a días; usa `Cast('posted_date', DateField())` para evitar bug de timezone (UTC vs Lima)
- `resultados_empleos` — simplificado: sin creación de registros `Busqueda`
- Filtro keyword busca directamente en `title` y `company` (en vistas que lo usan)

### URLs (`applications/empleos/urls.py`)
- `empleos/ocultas/` → `ofertas-ocultas`
- `empleos/toggle/<int:pk>/` → `toggle-oculto`

### Templates
- `buscar_empleo.html` — header con links a "Ocultas" y "Guardados"
- `empleos_guardados.html` — filtros: fuente (select), período (select: hoy/ayer/3d/1s/1m), columna "Acción" con botón ocultar; sin input keyword
- `ofertas_ocultas.html` — filtros: fuente, período; columna "Acción" con botón restaurar
- `resultados_empleos.html` — header con links a "Guardados" y "Nueva búsqueda"

### Bug corregido
- Filtro por fecha fallaba por conversión timezone: `posted_date` en UTC midnight (00:00:00+00:00) se convertía a Lima (UTC-5) como día anterior. Solución: `Cast('posted_date', DateField())` para comparar sin conversión timezone

---

## Ajustes página de Precios (12 ago 2026)

### Precio opcional
- `applications/home/models.py` — `Servicio.precio` ahora `null=True, blank=True`; `__str__` muestra "Sin precio" cuando no hay
- Migraciones: `0007_alter_servicio_precio` (nullable) y `0008_servicio_precios_parciales` (deja precio solo en Página Web Corporativa S/ 350 y Soporte Técnico Online S/ 60)
- `templates/home/precios.html` — bloque de precio condicional `{% if servicio.precio %}`; sin precio no se muestra texto (spacer `&nbsp;` para mantener ritmo visual); eliminado el subtexto "una sola vez · sin mensualidad"

### Servicios nuevos/modificados (data migrations)
- `0009_servicio_automatizaciones.py` — un solo servicio **"Automatizaciones para tu Negocio"** (`fas fa-robot`, purple, sin precio, orden 10) con 5 características
- `0010_servicio_quitar_soporte.py` — elimina el "tiempo de soporte" (1 semana/2 semanas/1 mes/3 meses de soporte) de las características de 5 servicios
- `0011_fusionar_ventas_inventario.py` — fusiona "Sistema de Ventas" + "Sistema de Inventario" en **"Sistema de Ventas e Inventario"** (7 características, conserva id/orden 2)
- `0012_servicio_catalogo_web.py` — nuevo **"Catálogo Web"** (`fas fa-book-open`, slate, sin precio, orden 3): catálogo digital con pedidos por WhatsApp

### Colores
- `0013_reorganizar_colores.py` — paleta reasignada por nombre:
  - Página Web Corporativa → blue · Catálogo Web → teal · Reservas y Citas → amber · Tienda Online → indigo · Sistema de Ventas e Inventario → emerald · Soporte Técnico Online → slate · Automatizaciones → purple

### Grid
- `templates/home/precios.html` — `lg:grid-cols-3` → `lg:grid-cols-4` (4 cards por fila)

---

## Nueva página de Precios `/precios/` (11 ago 2026)

Página de precios dinámica para ofrecer sistemas web con descripción y precio, gestionada desde el admin.

### Archivos nuevos
- `templates/home/precios.html` — página con hero, grid de cards (ícono, nombre, descripción, precio, características, badge "Recomendado") y CTA a WhatsApp
- `applications/home/migrations/0006_servicio.py` — migración del modelo `Servicio`

### Archivos modificados
- `applications/home/models.py` — modelo `Servicio` (nombre, descripción, precio, características JSON, ícono FontAwesome, color Tailwind, destacado, activo, orden) + mapa de clases `COLOR_CLASSES` y propiedad `clases`
- `applications/home/admin.py` — `ServicioAdmin` con `list_display`, `list_editable` (precio/destacado/activo/orden)
- `applications/home/views.py` — `PreciosView` (TemplateView) con contexto `servicios` (activos, ordenados)
- `applications/home/urls.py` — ruta `precios/` (name: `precios`)
- `templates/includes/header.html` — link "Precios" en el menú

### Corrección posterior
- Hero de `precios.html`: `-mt-[48px] lg:-mt-[60px] pt-[48px] lg:pt-[60px] pb-14` para eliminar la franja blanca entre el header fijo y la sección (mismo patrón del index)

### Datos de ejemplo (editables en admin)
- Página Web Corporativa `S/ 350`, Sistema de Ventas `S/ 800`, Inventario `S/ 650`, Reservas y Citas `S/ 550`, Tienda Online `S/ 1200` (destacado), Soporte Técnico `S/ 60`

---

## Estilo visual consistente (basado en `about_me.html`)

Patrón de diseño aplicado a todas las páginas:

- **Cards**: `border-radius: 1rem`, `box-shadow: 0 10px 24px rgba(15,23,42,.10)`, `border-left: 5px solid #2563eb`
- **Card hover**: `translateY(-3px)`, shadow incremento
- **Card headers**: `background: linear-gradient(135deg, #1e40af, #2563eb)`, `padding: 0.45rem 1rem`, `font-size: 0.9rem`
- **Heroes**: `border-radius: 1rem`, `background: linear-gradient(135deg, #0f172a 0%, #2563eb 55%, #1d4ed8 100%)`, `py-2`, `mb-4`
- **Colores**: primary `#2563eb`, dark navy `#1e40af`, sin `#007bff` ni `#ff00ee`
- **Espaciado general**: `mb-4` hero, `mb-3` entre cards

---

## Archivos modificados

### 1. `templates/home/about_me.html` (CREADO)
- Template nuevo con toda la info de `datos.html`
- Profile card: flex centrado, foto 150px, borde-radius 16px, borde azul
- Hero: título "Sobre Mí", gradiente azul
- Secciones: Experiencia, Proyectos, Educación, Skills, Idiomas

### 2. `templates/home/portafolio.html`
- Eliminado `body { background }` override
- Card headers con gradiente azul `#1e40af → #2563eb`
- Hover `translateY(-3px)`
- Hero: `py-2`, `mb-4`
- **Corregido bug**: indicadores de carousel no coincidían con items
  - P1: 10 → 14 indicadores
  - P2: 10 → 18 indicadores
  - P3: 10 → 12 indicadores

### 3. `templates/entrada/lista.html`
- Card headers con gradiente azul (eliminado `background-color: #007bff` inline)
- `border-radius: 1rem`
- Hover consistente `translateY(-3px)`
- Colores links/categorías: `#007bff` → `#2563eb`, `#ff00ee` → `#2563eb`

### 4. `templates/chat/home.html`
- Eliminado `body { background }` override
- Card `border-radius: 1rem`
- Header gradiente `#1e40af → #2563eb`
- Hover `translateY(-3px)`, dot verde `#22c55e`
- Toolbar `border-radius: 1rem`

### 5. `templates/amigos/lista_amigos.html`
- Hero con gradiente `#0f172a → #2563eb`
- Headers de sección gradiente azul compactos (#1e40af → #2563eb)
- Friend-card hover `translateY(-3px)`

### 6. `templates/amigos/perfil_red.html`
- Hero compacto `padding: 1rem`
- Post-card: `border-left: 5px solid #2563eb`, `border-radius: 1rem`
- Filtro-card con header gradiente azul
- Stat-card hover `translateY(-3px)`

### 7. `templates/entrada/profile_view.html` (`/users/1/`)
- Avatar: `border-radius: 16px` (antes `50%`)
- Panel: `shadow: 0 10px 24px rgba(15,23,42,.10)`, hover `translateY(-3px)`
- Section title: color `#1e40af` (antes `#334155`)
- Info-card: hover `translateY(-3px)`, shadow consistente
- Badges: compactos (`padding: 0.4rem 0.7rem`)
- Eliminado `body { background }` override

---

## Archivos clave del proyecto

| Archivo | Función |
|---|---|
| `templates/base.html` | Template base (Bootstrap 4, FA5, devicons) |
| `templates/includes/header.html` | Navbar compartida |
| `applications/home/views.py` | `AboutMe` (línea 38) |
| `applications/entrada/views.py` | `UserProfileView` (línea 288) |
| `applications/entrada/urls.py` | Ruta `users/<int:pk>/` (línea 64) |
| `datos.html` | Fuente de datos para about_me |

---

## Cambios realizados (17 jul 2026)

### 1. Color navy actualizado: `#1e3a8a` → `#1e40af`
Reemplazado en **12 archivos** (todos los que usaban el color navy):
- `templates/base.html` — variable `:root --navy`
- `templates/chat/room.html` — fondo body
- `templates/chat/home.html` — gradientes card-header
- `templates/home/index.html` — `:root`, gradientes, hover
- `templates/home/indexprueba.html` — bg-navy, btn-navy, gradientes
- `templates/home/index3.html` — `:root`, theme-color, print styles, JS
- `templates/home/about_me.html` — gradientes, color texto
- `templates/home/portafolio.html` — gradientes card-header
- `templates/amigos/perfil_red.html` — gradientes card-header
- `templates/amigos/lista_amigos.html` — gradientes card-header
- `templates/entrada/profile_view.html` — color texto
- `templates/entrada/lista.html` — gradientes, border-left

### 2. Tamaño de fuente base reducido
- `static/css/estilos.css`: `html { font-size: 16px; }` → `html { font-size: 15px; }`

### 3. Hero del index agrandado ~20%
- `templates/home/index.html`: todas las fuentes del hero incrementadas ~20%
  - h1: `display-4` + `font-size:3rem`
  - Badges: `.72rem/.8rem` → `.85rem/.95rem`
  - Subtítulo: `.92rem` → `1.1rem`
  - Párrafo: `.95rem` → `1.15rem`
  - Tech pills: `.78rem` → `.95rem`
  - Terminal: `.65rem/.78rem` → `.78rem/.95rem`

### 4. Hero del index más ancho
- `templates/home/index.html`: hero extraído del `<div class="container">` y envuelto en `<div class="container-fluid px-3 px-lg-5">` para mayor ancho horizontal
