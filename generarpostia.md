# Generar Posts con IA (Automatización)

## Objetivo
Automatizar la creación de posts del blog. El usuario indica un tema y la IA
genera título, resumen, contenido HTML, tags y categoría para crear borradores
rápidos que luego se revisan y publican.

## IA gratuita (2026)
| Opción | Costo | Límites | Nota |
|---|---|---|---|
| **Gemini (AI Studio)** ✅ | $0 | ~1,500 req/día, sin tarjeta | Ya configurado en `blog/settings.py` (`GEMINI_API_KEY`, `GEMINI_MODEL`). Caveat: los datos pueden entrenar a Google |
| **Groq** | $0 | ~1,000 req/día | Llama 3.3 70B, rápido, compatible con API de OpenAI, NO entrena con tus datos |
| **Mistral** | $0 | ~1 billón tokens/mes | Requiere verificación telefónica |
| **Ollama (local)** | $0 ilimitado | Sin límites, offline | Requiere RAM/GPU (solo CPU = lento) |

Decisión: usar **Gemini** vía REST con `requests` (ya instalado), sin
dependencias nuevas.

## Cambios
1. `applications/entrada/services.py` (nuevo)
   - `generar_post_con_ia(tema) -> {title, resume, content_html, tags, category}`
   - Llama a Gemini REST: `POST {GEMINI_MODEL}:generateContent?key=...`
   - Prompt que pide JSON estructurado para poder rellenar el formulario.
2. `applications/entrada/models.py` + migración
   - Hacer `Entry.image` opcional (`null=True, blank=True`) → imagen queda pendiente.
3. Management command `crear_post`
   - `python manage.py crear_post --tema "..."` crea borradores en lote
     (`public=False`), siguiendo el patrón de `applications/empleos`.
4. Botón "Generar con IA" en `templates/entrada/agregar.html`
   - Input de tema + botón → llama al servicio → rellena
     título/resumen/tags/categoría/contenido (CKEditor) para revisar antes de guardar.

## Pendientes / Notas
- Verificar que `.env` tenga una `GEMINI_API_KEY` válida
  (key de IAs gratis: https://aistudio.google.com/apikey). El historial del repo
  ya mostró "quota exceeded" con gemini-2.0-flash free tier.
- El post se guarda como borrador hasta que el usuario lo publique y suba imagen.