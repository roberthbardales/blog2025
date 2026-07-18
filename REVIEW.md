# Blog2025 — Resumen de avances

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
