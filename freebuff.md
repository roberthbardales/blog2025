# Revisión Completa del Proyecto `blog2025`

**Fecha:** 15 de julio, 2026  
**Revisado por:** Buffy (Freebuff)

---

## Resumen General

Proyecto Django 3.2.25 con Bootstrap 5, PostgreSQL, WebSockets (Channels/Daphne), Firebase Auth, REST API (DRF + JWT), chat en tiempo real, sistema de amigos/favoritos, notas adhesivas. **Buena arquitectura base, pero con issues pendientes y oportunidades de mejora.**

---

## Arquitectura

| Componente | Tecnología |
|------------|------------|
| **Framework** | Django 3.2.25 |
| **Base de datos** | PostgreSQL (psycopg2-binary) |
| **Auth** | Modelo custom `User` (email como USERNAME_FIELD) + Firebase backend |
| **WebSockets** | Channels 4 + Daphne |
| **API REST** | DRF + SimpleJWT |
| **Frontend** | Django Templates + Bootstrap 5 + CKEditor |
| **Email** | SMTP (Gmail) |
| **IA** | Gemini API (chatbot, deshabilitado) |

### Apps activas
- `users` - Autenticación y gestión de usuarios
- `home` - Landing page, visitas, contacto
- `entrada` - Blog entries, categorías, tags, likes, comentarios
- `favoritos` - Sistema de favoritos
- `chat` - Chat en tiempo real con estado online/offline
- `notas` - Notas adhesivas personales
- `amigos` - Sistema de amigos y solicitudes

### Apps deshabilitadas
- `rag` - Sentence Transformers + Ollama (100% comentado)
- `chatbot` - Búsqueda por keywords + Gemini API (comentada en INSTALLED_APPS)

---

## 🚨 Issues Críticos (Requieren Atención Inmediata)

| # | Issue | Ubicación | Impacto |
|---|-------|-----------|---------|
| 1 | **`OTRO` constante definida dos veces** en `User` model | `applications/users/models.py:11,15` | La segunda definición (`'O'`) sobreescribe la primera (`'2'`), rompiendo `OCUPATION_CHOICES` - el valor `'2'` (Otro) nunca se muestra correctamente |
| 2 | **`@csrf_exempt` sin justificación** en endpoints sensibles | `chat/views.py:108`, `users/views.py` (FirebaseLoginView) | Seguridad comprometida - debería usar DRF permissions o rate limiting |
| 3 | **APIs externas en context processors** (cada request HTTP) | `applications/processors.py` | Llama a `ipapi.co` y `open-meteo.com` en **cada carga de página** - rendimiento severo |
| 4 | **`VisitorCreateView` incompleta** | `applications/home/views.py:92-103` | Código muerto: `# VisitorLog.objects.create(ip=ip, ...)` comentado |
| 5 | **Import duplicado** `Entry` | `applications/amigos/views.py:2,9` | Código limpio comprometido |

---

## ⚠️ Issues de Seguridad

| Issue | Detalle |
|-------|---------|
| `@csrf_exempt` en `ping` | Endpoint POST sin protección CSRF - podría ser explotado |
| `FirebaseLoginView` sin rate limiting | `authentication_classes = []` y `permission_classes = []` - intencional para auth inicial, pero sin throttling |
| `DEBUG` flag handling | Correcto (usa env), pero `processors.py` hardcodea "Lima"/"PE" en DEBUG |
| `CHANNEL_LAYERS` en `InMemoryChannelLayer` | Solo para desarrollo - **no escala en producción** |

---

## 🐛 Bugs y Problemas de Lógica

| Bug | Descripción |
|-----|-------------|
| `OTRO` duplicado | `OCUPATION_CHOICES` usa `'2'` pero `GENDER_CHOICES` usa `'O'` - segunda definición sobreescribe |
| `VisitorCreateView` incompleta | Endpoint AJAX para registrar visitas está comentado internamente |
| `processors.py` hace HTTP requests | Cada visitante ejecuta 2 llamadas HTTP externas por carga de página |
| Sin paginación en chat | Solo últimos 50 mensajes, sin "cargar más" |

---

## 📊 Arquitectura y Calidad de Código

### ✅ Fortalezas

- Buena separación en apps (`users`, `entrada`, `chat`, `amigos`, `notas`, `favoritos`)
- Uso correcto de CBVs con mixins (`LoginRequiredMixin`, `AdministradorPermisoMixin`)
- Modelo custom User con Firebase backend
- JWT configuración correcta (DRF + SimpleJWT)
- Rate limiting en `ping` (5s) para reducir writes
- Middleware de visitas funcional
- Sistema de amigos completo (solicitudes, aceptar, rechazar, bloquear)

### ❌ Debilidades

- Naming inconsistente (mezcla español/inglés: `buscador_general`, `obtener_ip`, `VisitorLogsView`)
- `processors.py` hace trabajo de middleware (HTTP requests externos)
- `chat/views.py` mezcla CBVs y FBVs inconsistentemente
- Código muerto y imports duplicados sin limpiar
- `rag/` app comentada pero con migraciones

---

## 📦 Dependencias y Configuración

| Aspecto | Estado |
|---------|--------|
| Django 3.2.25 | ⚠️ **EOL** - soporte de seguridad terminó abril 2024 |
| Channels 4.0.0 | ✅ Actual |
| DRF 3.15.1 | ✅ Actual |
| Firebase Admin 6.8.0 | ✅ Actual |
| Pillow 9.5.0 | ⚠️ Desactualizado (latest 10.x) |
| `requirements.txt` | ⚠️ Sin hashes de seguridad, versiones muy específicas |

---

## 🎨 Frontend (Templates/CSS)

| Aspecto | Estado |
|---------|--------|
| Bootstrap 5 | ✅ Correcto |
| `base.html` carga BS4 **y** BS5 | ❌ **Conflicto** - ambos JS cargados (lines 264-267) |
| Landing `index.html` | ✅ Bien diseñado con ScrollReveal |
| Responsive | ✅ Ajustes mobile implementados |
| Google Fonts Inter | ✅ Cargado correctamente |

---

## 📋 Resumen de Issues Pendientes (5 confirmados)

| # | Issue | Estado |
|---|-------|--------|
| 14 | `OTRO` duplicado en User model | ⚠️ Confirmado |
| 15 | RAG app comentada con migraciones | ⚠️ Confirmado |
| 16 | Chatbot sin autenticación si se activa | ⚠️ Confirmado |
| 17 | Mezcla BS4/BS5 en base.html | ⚠️ Confirmado |
| 18 | Archivos huérfanos en raíz | ⚠️ Confirmado |

### Issues Corregidos (13)

| # | Issue | Estado |
|---|-------|--------|
| 1 | `processors.py` — `obtener_ip` hardcodea en DEBUG | ✅ Corregido |
| 2 | `entrada/managers.py` — `buscador_general` filtra con QuerySet | ✅ Corregido |
| 3 | `entrada/models.py` — `Entry.save()` rompe slug en cada edición | ✅ Corregido |
| 4 | `settings.py` — `SIMPLE_JWT` duplicado | ✅ Corregido |
| 5 | `ChatRoomView` sin paginación | ✅ Corregido |
| 6 | `favoritos/views.py` — `EntryListView` duplicado | ✅ Corregido |
| 7 | `amigos/views.py` — `PerfilRedView` expone drafts | ✅ Corregido |
| 8 | `chat/` — `is_read` nunca se actualiza | ✅ Corregido |
| 9 | `chat/` — `ping` sin rate limiting | ✅ Corregido |
| 10 | `VisitorLogMiddleware` solo logea `/` | ✅ Corregido |
| 11 | `ContactCreateView` vs `ContactCreateView2` | ✅ Corregido |
| 12 | `UpdatePasswordForm` naming confuso | ✅ Corregido |
| 13 | `processors.py` — typo en nombre | ✅ Corregido |

---

## 🎯 Recomendaciones Prioritarias

1. **Corregir `OTRO` duplicado** - Bug activo que afecta datos
2. **Migrar `processors.py` a middleware con caché** - Rendimiento crítico
3. **Eliminar código muerto** (`VisitorCreateView` incompleta, imports duplicados)
4. **Actualizar Django** a 4.2 LTS (soporte hasta abril 2026)
5. **Limpiar archivos huérfanos** de la raíz
6. **Decidir destino** de `rag/` y `chatbot/` (eliminar o activar)
7. **Migrar completamente a Bootstrap 5** (quitar BS4)

---

## Últimos Cambios (jun-jul 2026)

### Landing (jun 2026)
- Rediseño completo con paleta navy `#1e3a8a` + ocean `#3b82f6`
- Hero full-viewport con gradient y glassmorphism
- Cards con icon-box coloreados por categoría
- ScrollReveal para animaciones fade-up
- Google Fonts Inter agregado

### Corrección de issues (jul 2026)
- `VisitorLogMiddleware` - Excluye `/static/`, `/media/`, `/admin/`, `/api/`
- `ContactCreateView` - Consolidada en una sola versión
- `UpdatePasswordForm` - Campos renombrados a `current_password` y `new_password`
- `processors.py` - Renombrado de `procesors.py`
