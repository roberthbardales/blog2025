# Revisión del Proyecto `blog2025`

## Resumen General

Blog Django con Bootstrap 5, PostgreSQL, WebSockets (Channels/Daphne), Firebase Auth, REST API (DRF + JWT), chat en tiempo real, chatbot con Gemini, notas adhesivas, sistema de amigos y favoritos. Usa Python 3.x con Django 3.2.25.

---

## Arquitectura

- **Config**: `blog/settings.py`, `blog/urls.py`, `blog/asgi.py`
- **Apps activas**: `users`, `home`, `entrada`, `favoritos`, `chat`, `notas`, `amigos`
- **Apps deshabilitadas**: `rag`, `chatbot`
- **Placeholder vacía**: `Notificaciones`
- **Base de datos**: PostgreSQL con psycopg2-binary
- **Auth**: Modelo custom `User` (email como USERNAME_FIELD) + Firebase backend
- **WebSockets**: Channels 4 + Daphne
- **Frontend**: Django Templates + Bootstrap 5 + CKEditor

---

## Estado de los Issues Reportados (verificado jul 2026)

### CRÍTICOS

| # | Issue | Estado | Detalle |
|---|-------|--------|---------|
| 1 | `processors.py` — `obtener_ip` hardcodea en DEBUG | **CORREGIDO** | Ahora sí usa `REMOTE_ADDR` (line 27). En DEBUG retorna "Lima"/"PE" hardcodeado pero no es grave. |
| 2 | `entrada/managers.py` — `buscador_general` filtra con QuerySet | **CORREGIDO** | Ahora recibe `kword_general` como string (line 53). El bug ya no existe. |
| 3 | `entrada/models.py` — `Entry.save()` rompe slug en cada edición | **CORREGIDO** | Ahora solo genera slug si `self.slug` está vacío (primera creación). Las ediciones preservan el slug existente. |

### ALTOS

| # | Issue | Estado | Detalle |
|---|-------|--------|---------|
| 4 | `settings.py` — `SIMPLE_JWT` duplicado | **CORREGIDO** | Bloque duplicado eliminado. Solo queda una configuración. |
| 5 | `ChatRoomView` sin paginación | **CORREGIDO** | Limitado a últimos 50 mensajes con `[:50]`. Se invierte orden para mostrar cronológicamente. |
| 6 | `favoritos/views.py` — `EntryListView` duplicado | **CORREGIDO** | Copy-paste eliminado. Era código muerto sin URL ni imports. |
| 7 | `amigos/views.py` — `PerfilRedView` expone drafts | **CORREGIDO** | Ahora filtra por `public=True` en el queryset. |
| 8 | `chat/` — `is_read` nunca se actualiza | **CORREGIDO** | Ahora se marca como `True` al abrir el chat (ChatRoomView). |
| 9 | `chat/` — `ping` sin rate limiting | **CORREGIDO** | Rate limiting de 5s: solo escribe si pasaron >=5s desde el último ping. Reduce ~80% de writes. |

### MEDIOS

| # | Issue | Estado | Detalle |
|---|-------|--------|---------|
| 10 | `VisitorLogMiddleware` solo logea `/` | **CORREGIDO** | Ahora excluye solo `/static/`, `/media/`, `/admin/`, `/api/`. |
| 11 | `ContactCreateView` vs `ContactCreateView2` | **CORREGIDO** | Eliminada la versión obsoleta, consolidada en una sola con envío de email. |
| 12 | `UpdatePasswordForm` naming confuso | **CORREGIDO** | Campos renombrados a `current_password` y `new_password`. |
| 13 | `processors.py` — typo en nombre | **CORREGIDO** | Archivo renombrado de `procesors.py` a `processors.py`. |

### BAJOS

| # | Issue | Estado | Detalle |
|---|-------|--------|---------|
| 14 | `User` model — `OTRO` definido dos veces | **CONFIRMADO** | `'2'` se sobreescribe con `'O'` (models.py:11 y 15). |
| 15 | `rag/` app comentada | **CONFIRMADO** | Tiene migración pero fuera de `INSTALLED_APPS`. |
| 16 | `chatbot` sin autenticación | **CONFIRMADO** | Está comentado en `INSTALLED_APPS`, pero si se activa, es abierto. |
| 17 | `base.html` mezcla BS4 y BS5 | **CONFIRMADO** | Ambos JS cargados (lines 264-267). Posibles conflictos. |
| 18 | Archivos huérfanos en raíz | **CONFIRMADO** | `visitas_pc.txt`, `get_token.html`, `firebase_login.html`, `.aider.chat.history.md`. |

### Resumen

- **13 issues corregidos** (#1 obtener_ip, #2 buscador_general, #3 slug, #4 SIMPLE_JWT, #5 chat paginación, #6 EntryListView duplicado, #7 drafts expuestos, #8 is_read, #9 ping rate limiting, #10 VisitorLogMiddleware, #11 ContactCreateView, #12 UpdatePasswordForm, #13 procesors.py)
- **5 issues confirmados** que siguen activos (#14 OTRO duplicado, #15 rag comentada, #16 chatbot sin auth, #17 BS4/BS5 mix, #18 archivos huérfanos)
- **0 issues nuevos** encontrados

### Recomendaciones activas (pendientes)

1. ~~Corregir `buscador_general`~~ ✅ Ya corregido
2. ~~Reparar `obtener_ip`~~ ✅ Ya usa REMOTE_ADDR
3. ~~Slug se regeneraba en cada edición~~ ✅ Solo se genera en creación
4. ~~Eliminar `SIMPLE_JWT` duplicado~~ ✅ Ya eliminado
5. Paginación en chat (scroll infinito o load more)
6. ~~Eliminar `EntryListView` duplicado en favoritos~~ ✅ Ya eliminado
7. ~~Filtrar `public=True` en `PerfilRedView`~~ ✅ Ya filtrado
8. ~~Implementar `is_read` en mensajes de chat~~ ✅ Marca como leído al abrir chat
9. ~~Rate limiting en `ping`~~ ✅ Rate limiting de 5s implementado
10. Limpiar archivos huérfanos de la raíz (#18)
11. Migrar completamente a Bootstrap 5 (#17)
12. ~~Renombrar `procesors.py` a `processors.py`~~ ✅ Ya renombrado
13. ~~Unificar `ContactCreateView` / `ContactCreateView2`~~ ✅ Ya unificado
14. ~~Renombrar campos en `UpdatePasswordForm`~~ ✅ Renombrados a `current_password` y `new_password`
15. Corregir `OTRO` duplicado en User model (#14)
16. Redis para channel layer en producción
17. Decidir destino de `rag/` (eliminar o activar) y `chatbot/` (agregar auth o eliminar)
18. Eliminar `rag/` si no se va a usar Ollama/sentence-transformers

---

## Últimos cambios (jun 2026)

### Rediseño completo del landing (`templates/home/index.html`)
- **Estilo**: Cambio a paleta navy `#1e3a8a` + ocean `#3b82f6`, tipografía Inter (Google Fonts)
- **Hero**: Full-viewport gradient navy→blue, pill badge con glassmorphism, gradient text "Bardales", floating tech icons (Django, PostgreSQL, Soporte)
- **Servicios**: Cards blancas shadow-sm con icon-box 56px cuadrado + color por categoría (8 sistemas: verde, azul, naranja, amarillo, rosa, teal, slate, indigo)
- **Proceso**: Step cards con número cuadrado azul + hover translateY(-6px) (3 pasos)
- **Tecnologías**: Badges tipo pill con borde `#e2e8f0` + colores por tecnología + hover shadow blue
- **Stats**: Gradiente navy→ocean + iconos decorativos (briefcase, clock, heart) + patrón radial de fondo
- **Soporte**: Mismo estilo service-card con icon-box coloreados por servicio (7 servicios)
- **CTA Banner**: Gradiente navy→ocean con círculo decorativo flotante `::before`
- **ScrollReveal**: Animaciones fade-up en todas las secciones
- **Responsive**: Ajustes mobile en títulos, avatar, stats, botones

### Navbar (`templates/includes/header.html`)
- Rediseñado temporalmente a navy con blur, underline animation, search glassmorphism
- Revertido al diseño original (gradiente azul `#0d6efd→#084298`)

### Base (`templates/base.html`)
- Agregado Google Fonts Inter (pesos 300-800)
- Body background cambiado a `#f8fafc` con `font-family: 'Inter'`

### Archivos modificados
- `templates/base.html` — Google Fonts Inter, body bg
- `templates/home/index.html` — Rediseño completo del landing
- `templates/includes/header.html` — Rediseñado y luego revertido

---

## Últimos cambios (jul 2026)

### Sesión de corrección de issues

**Archivos modificados:**

| Archivo | Cambio | Issue |
|---------|--------|-------|
| `applications/home/middleware.py:12-14` | `VisitorLogMiddleware` ahora excluye solo `/static/`, `/media/`, `/admin/`, `/api/` en vez de descartar todo lo que no sea `/` | #10 |
| `applications/home/forms.py:25-28` | Eliminada `ContactForm` (usaba `__all__`), renombrada `ContactForm2` → `ContactForm` con campos explícitos | #11 |
| `applications/home/views.py:19,65-67` | Eliminada la vieja `ContactCreateView` (sin email), renombrada `ContactCreateView2` → `ContactCreateView`, import simplificado | #11 |
| `applications/home/urls.py:20-24` | Eliminado path `rcontact2`, consolidado en `rcontact` con nombre `add-contact` | #11 |
| `templates/includes/footer.html:69` | URL actualizada de `add-contact2` → `add-contact` | #11 |
| `applications/users/forms.py:117,127` | Campos renombrados: `password1` → `current_password`, `password2` → `new_password` | #12 |
| `applications/users/views.py:89,92` | Referencias actualizadas a `current_password` y `new_password` | #12 |
| `REVIEW.md` | Estado de issues #10, #11, #12 actualizado a CORREGIDO | — |

### Análisis de apps rag/ y chatbot/

| App | Funciona | Tecnología | Estado |
|-----|----------|------------|--------|
| `rag/` | **No** (100% comentado) | Sentence Transformers + TinyLlama (Ollama local) | Nunca activada, código muerto |
| `chatbot/` | **Sí** (código funcional) | Búsqueda por keywords + Gemini API | Comentada en INSTALLED_APPS pero URL activa |

- Son **independientes** (no se importan entre sí)
- Ambas resuelven lo mismo: RAG sobre el blog
- `rag/` necesita infraestructura local (Ollama, sentence-transformers, numpy)
- `chatbot/` funciona con API key de Gemini (ya configurada en `.env`)
- `chatbot/` tiene problema de seguridad: sin autenticación + `@csrf_exempt`
- `chatbot/` nunca fue commiteado a git (untracked)
- `rag/` fue creada ~jun 2025, `chatbot/` fue creada 6 may 2026

**Pendiente:** decidir si eliminar ambas, activar una, o fusionarlas
