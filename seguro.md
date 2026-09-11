# Seguridad de producción — Endurecer con HTTPS puro

Guía para aplicar configuraciones de seguridad sugeridas por `manage.py check --deploy`
en `blog/settings.py`. El objetivo es que el sitio funcione solo por HTTPS (SSL).

> Estado: **pendiente de aplicar**. Revisar antes de ejecutar, especialmente el punto de
> verificación de HTTPS en el VPS.

---

## Configuraciones y qué hacen

| Config | Advertencia | Qué hace |
|--------|-------------|----------|
| `SECURE_SSL_REDIRECT = True` | `security.W008` | Redirige todo el tráfico HTTP a HTTPS |
| `SESSION_COOKIE_SECURE = True` | `security.W012` | La cookie de sesión solo viaja por HTTPS |
| `CSRF_COOKIE_SECURE = True` | `security.W016` | La cookie de CSRF solo viaja por HTTPS |
| `SECURE_HSTS_SECONDS` | `security.W004` | Obliga al navegador a usar solo HTTPS durante N segundos |

---

## CRÍTICO: verificar HTTPS antes de activar

Todo esto exige que el **VPS ya sirva HTTPS** (nginx + certbot / certificado SSL).

Sin HTTPS funcionando:
- `SESSION_COOKIE_SECURE` / `CSRF_COOKIE_SECURE` → **rompen el login** (la cookie nunca se envía).
- `SECURE_SSL_REDIRECT` → **rompe el acceso** (depende del proxy para redirigir).
- `SECURE_HSTS_SECONDS` alto de golpe → puede **bloquear el sitio** por mucho tiempo.

Pasos previos:
1. Confirmar que `https://tusitio` responde y el certificado es válido.
2. Configurar `ALLOWED_HOSTS` con el dominio en `.env`.
3. Tener `DEBUG = False` en producción.
4. Generar un `SECRET_KEY` largo y aleatorio (>50 caracteres).

---

## Plan de implementación gradual (recomendado)

### Fase 1 — Cookies seguras (sin redirección aún)
```python
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```
Probar login y formularios por HTTPS. Confirmar que todo funciona antes de continuar.

### Fase 2 — Forzar HTTPS
```python
SECURE_SSL_REDIRECT = True
```

### Fase 3 — HSTS incremental (subir de a poco)
Empieza bajo y ve subiendo en despliegues sucesivos, verificando que HTTPS nunca falle:
```python
SECURE_HSTS_SECONDS = 60          # primera prueba
SECURE_HSTS_SECONDS = 3600        # tras confirmar estabilidad
SECURE_HSTS_SECONDS = 31536000    # 1 año, solo al final
SECURE_HSTS_INCLUDE_SUBDOMAINS = True   # solo al final
SECURE_HSTS_PRELOAD = True              # solo al final
```

> Advertencia: si bajas HSTS después de haberlo fijado alto, los navegadores podrían
> bloquear el sitio por el tiempo configurado. Por eso es incremental.

---

## Cómo implementarlo (usando `.env` para no tocar settings a mano)

`blog/settings.py` ya usa `django-environ`. Añadir al final de settings.py:

```python
# -------------------------------
# Seguridad HTTPS (producción)
# -------------------------------
SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', default=False)
SESSION_COOKIE_SECURE = env.bool('SESSION_COOKIE_SECURE', default=False)
CSRF_COOKIE_SECURE = env.bool('CSRF_COOKIE_SECURE', default=False)
SECURE_HSTS_SECONDS = env.int('SECURE_HSTS_SECONDS', default=0)
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool('SECURE_HSTS_INCLUDE_SUBDOMAINS', default=False)
SECURE_HSTS_PRELOAD = env.bool('SECURE_HSTS_PRELOAD', default=False)
```

Y en `.env` activarlo por fases:
```ini
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=0
```

---

## Verificación post-implementación

1. `python manage.py check --deploy` → las advertencias W004/W008/W012/W016 deben desaparecer.
2. `python manage.py check` → 0 issues.
3. Probar:
   - `https://tusitio` carga bien.
   - Login y envío de formularios funcionan.
   - `http://tusitio` redirige a HTTPS (Fase 2 en adelante).

---

## Recordatorio antes de desplegar en el VPS

Aplicar en `.env` del VPS (no solo local), reiniciar el servicio (gunicorn/daphne/systemd)
y verificar con el `check --deploy`. Mantener backup de `.env` del VPS por si hay que revertir.
