# Especificación: App móvil de Empleos (React Native)

Documento generado a partir del módulo `applications/empleos` del proyecto Django blog2025.
Objetivo: crear una app **100% React Native**, **sin sistema de usuarios**, que consuma directamente la API externa de empleos y replique toda la funcionalidad actual del módulo web.

---

## 1. Descripción general

La app permite:

1. **Buscar ofertas de empleo** en una API externa (cvmatcher / getinjob) aplicando filtros.
2. **Guardar los resultados** localmente en el dispositivo, marcando cuáles son nuevas respecto a búsquedas anteriores.
3. **Listar las ofertas guardadas** con filtros locales (palabra clave, fuente, periodo de publicación).
4. **Ocultar/restaurar ofertas** (las ocultas van a una sección aparte).
5. Extras: historial de palabras clave buscadas, badge "Nueva" según última visita.

No hay backend propio ni login de usuarios: todo se consume directo de la API externa y se persiste en el dispositivo.

---

## 2. API externa (integración principal)

### 2.1 Configuración base

| Constante | Valor |
|---|---|
| `API_URL` | `https://api.getinjob.app/` |
| `PAGE_SIZE` | `25` |
| `TIMEOUT` | `30` segundos |
| `MAX_RETRIES` | `3` intentos por página |
| `RETRY_WAIT` | `2` segundos entre reintentos |
| Credenciales | email y password (ver sección 6) |

### 2.2 Autenticación

```
POST {API_URL}auth/login/
Content-Type: application/json

{ "email": "<CVM_EMAIL>", "password": "<CVM_PASSWORD>" }
```

- Respuesta 200: `{ "token": "<jwt>" }`
- El token se envía en cada búsqueda como `Authorization: Bearer <token>`.
- En la app: hacer login una vez al iniciar, cachear el token y re-loguear si una búsqueda devuelve 401.

### 2.3 Headers obligatorios (todas las requests)

```
Content-Type: application/json
x-client-key: UnN3YUFWNHRpZzY5bEhzenV1YjRQQzRnTkpVdTF0
x-client-version: 1.0.0
x-platform: cvmatcher
x-client-data: <base64 de fecha/hora actual>
Origin: https://dashboard.cvmatcher.app
Referer: https://dashboard.cvmatcher.app/
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36
Authorization: Bearer <token>   ← solo en jobs/search
```

**`x-client-data`**: fecha/hora actual en zona horaria `America/Lima`, formateada como
`{mes}/{dia}/{año}, {hh:mm:ss AM/PM}` (hora con 2 dígitos, mes/día sin padding), luego codificada en base64.

Ejemplo JS:

```js
function clientDataHeader() {
  const now = new Date(); // ajustar a America/Lima (ej. con Intl o dayjs.tz)
  const formatted = `${now.getMonth() + 1}/${now.getDate()}/${now.getFullYear()}, ` +
    now.toLocaleTimeString('en-US', { hour12: true, hour: '2-digit', minute: '2-digit', second: '2-digit' });
  return base64Encode(formatted); // ej. "8/20/2026, 03:45:12 PM"
}
```

### 2.4 Búsqueda de ofertas

```
POST {API_URL}jobs/search?page={pagina}&size=25&with_match=true
Authorization: Bearer <token>
```

Body JSON — incluir solo los filtros que tengan valor:

```json
{
  "job": ["python developer"],
  "country_id": 1,
  "from_age": 1,
  "type_order": 1,
  "job_seniority": [1, 2, 3],
  "work_modality_id": [1],
  "job_category_id": [5],
  "job_type_id": [2],
  "salary_min": 1000,
  "salary_max": 5000,
  "currency_type": "PEN",
  "p_english_req": false
}
```

Tipos: `job` es array de strings; `country_id`, `from_age`, `type_order`, `salary_min/max` son enteros; `job_seniority`, `work_modality_id`, `job_category_id`, `job_type_id` son arrays de enteros; `p_english_req` booleano.

Respuesta exitosa (200 o 201):

```json
{
  "count": 120,
  "data": [
    {
      "id": "...",
      "url": "https://...",
      "title": "Python Developer",
      "company": "ACME",
      "location": "Lima",
      "salary_min": 3000,
      "salary_max": 5000,
      "currency_type": "PEN",
      "posted_date": "2026-08-19T14:30:00Z",
      "company_logo": "https://.../logo.png",
      "technical_skills": ["Python", "Django", "SQL"]
    }
  ]
}
```

Campos usados de cada job:

| Campo app | Fuente en respuesta |
|---|---|
| `api_id` | `id` (fallback: la propia `url`) |
| `title` | `title` (fallback: "Sin título") |
| `company` | `company` |
| `location` | `location` |
| `salary_min` / `salary_max` / `currency_type` | homónimos |
| `posted_date` | `posted_date` (parsear ISO; reemplazar `Z` por `+00:00`) |
| `source` | derivado de `url` (ver 3.2) |
| `logo_url` | primer valor no vacío de: `company_logo`, `logo_url`, `logo`, `company_image`, `image` |
| `skills` | `technical_skills` recortado a máximo **8** elementos |
| `level_rank` / `level` | derivado de `title` (ver 3.1) |

**Importante**: si un job no tiene `url`, descartarlo.

### 2.5 Lógica de paginación y reintentos

Replicar el comportamiento de `buscar_ofertas(filtros, max_pages)`:

1. Login → token.
2. Loop `page = 1..max_pages` (la web usa default 3, máximo permitido 10).
3. Por página: hasta 3 intentos con espera de 2s entre fallos. Si la página falla definitivamente, **cortar el loop sin error fatal** (devolver lo acumulado).
4. Acumular resultados en un mapa clave = `url` (deduplicación).
5. Cortar el loop si: `jobs_de_pagina < 25` O `count == 0` O `page * 25 >= count`.
6. Devolver valores únicos del mapa.

---

## 3. Reglas de negocio

### 3.1 Detección de nivel (por regex sobre el título, case-insensitive)

Evaluar en orden; el primer match gana. Si nada coincide → rank 5, "Sin nivel".

| Rank | Nivel | Regex |
|---|---|---|
| 1 | Prácticas | `\bpracticante\b\|\btrainee\b\|\bpasante\b\|\bbecario\b\|\bpre[- ]?profesional\b` |
| 2 | Junior | `\bj[úu]nior\b\|\bjr\.?\b\|\bjun\.\b` |
| 3 | Semi Senior | `\bsemi[- ]?(?:senior\|s?r)\.?\b\|\bssr\.?\b` |
| 4 | Senior | `\bsenior\b\|\bsr\.?\b\|\bstaff\b\|\blead\b\|\bprincipal\b\|\barchitect\b\|\btech[- ]?lead\b\|\bexperto\b` |
| 5 | Sin nivel | — |

### 3.2 Detección de fuente (por dominio de la URL)

Extraer dominio de la URL, buscar coincidencia de clave dentro del dominio:

| Clave en dominio | Fuente mostrada |
|---|---|
| `computrabajo` | Computrabajo |
| `indeed` | Indeed |
| `linkedin` | LinkedIn |
| `bumeran` | Bumeran |
| `workdayjobs` / `myworkdayjobs` | Workday |
| `yondur` | Yondur |
| `supersol` | SuperSol |
| `coppel` | Coppel |
| `jobs` | Portal de empleo |

Fallback: quitar `www.`, tomar la primera parte antes del punto y capitalizarla.

### 3.3 Catálogos fijos

**Países** (`country_id`): `1`=Perú, `2`=México, `3`=Colombia, `4`=Chile, `5`=Argentina, `6`=España.

**Niveles seniority** (`job_seniority`): `1`=Prácticas, `2`=Junior, `3`=Semi Senior, `4`=Senior.

**Periodos locales** (filtro de guardados): `hoy`=0 días, `ayer`=1, `3d`=3, `1s`=7, `1m`=30 (restar días a hoy y filtrar por fecha de `posted_date`).

### 3.4 Ordenamientos

- **Resultados de búsqueda**: primero las ofertas nuevas (no existían localmente), luego las ya registradas; dentro de cada grupo por `posted_date` descendente.
- **Guardados / Ocultas**: por `posted_date` descendente.

---

## 4. Almacenamiento local en el dispositivo

Reemplaza a PostgreSQL. Opciones: `AsyncStorage` (JSON) o SQLite (`expo-sqlite`). Estructura lógica equivalente al modelo `OfertaEmpleo`:

```ts
interface OfertaEmpleo {
  api_id: string;        // único, índice
  title: string;
  company: string;
  location: string;
  salary_min: number | null;
  salary_max: number | null;
  currency_type: string;
  posted_date: string | null; // ISO
  source: string;
  logo_url: string;
  skills: string[];      // máx 8
  level_rank: number;    // 1-5
  level: string;
  url: string;           // único
  oculto: boolean;       // default false
  created: string;       // fecha de registro local (auto)
}
```

Operaciones:

- **Guardar resultados de búsqueda**: `upsert` por `api_id`. Si no existía → marcar `es_nueva=true`; si existía → actualizar campos manteniendo `oculto` y `created`.
- **Toggle oculto**: invertir `oculto` y persistir (sin recargar la lista: actualizar estado en memoria).
- **Filtro keyword** (guardados/ocultas): dividir el texto en palabras; match si **alguna** palabra aparece (case-insensitive) en `title`, `company`, `location`, `level`, `source` o dentro del array `skills`.
- **Filtro fuente**: `source === fuente` (lista de fuentes = valores distintos existentes).
- **Filtro periodo**: `fecha(posted_date) >= hoy - dias` según catálogo 3.3.

Claves adicionales en almacenamiento:

| Clave | Contenido |
|---|---|
| `empleos_keywords_history` | array de strings, máx **10**, más reciente primero, sin duplicados (case-insensitive). Se agrega al enviar búsqueda/filtro; los chips permiten reutilizar o borrar del historial. |
| `empleos_last_guardados_visit` | timestamp (ms) de la última visita a "Guardados". Una oferta cuyo `created > timestamp_anterior` muestra badge **"Nueva"**. Al salir de la pantalla, guardar el timestamp actual. |

---

## 5. Pantallas React Native

Stack sugerido: `axios` (con interceptor de login/token), `@react-native-async-storage/async-storage` o `expo-sqlite`, `@react-navigation/native`, `Linking` para abrir URLs externas.

### 5.1 Buscar
- Input "Palabras clave" + chips de historial debajo (tocar chip = rellenar input; X = borrar del historial).
- Select País (default Perú), Select Antigüedad (`""`=cualquier fecha, `1`=último día **default**, `3`, `7`, `30`).
- Input numérico "Máximo de páginas" (default 3, min 1, máx 10).
- Checkboxes de nivel: Prácticas ✅, Junior ✅, Semi Senior ✅, Senior ⬜ (defaults de la web).
- Botón "Buscar ofertas" → llama a la API paginando (mostrar spinner; puede tardar varios segundos).

### 5.2 Resultados
- Barra resumen: total de ofertas, texto buscado, chip de país, chips de niveles aplicados, contadores "**N** nuevas" y "**N** ya registradas".
- Lista/tarjetas por oferta: título (link externo), empresa, ubicación, chip de nivel coloreado, fuente, badge "Nueva"/"Ya registrada", icono de enlace externo (`Linking.openURL`).
- Colores del chip de nivel: rank 4 → azul, 3 → morado, 2 → verde, 1 → ámbar, otro → gris.
- Acceso rápido a "Guardados" y "Nueva búsqueda".

### 5.3 Guardados
- Filtros locales: input keyword (con chips de historial), select Fuente ("Todas" + fuentes distintas registradas), select Publicación (Todas/Hoy/Ayer/Hace 3 días/Hace una semana/Hace un mes), botón Filtrar y Limpiar.
- Texto contador: "N ofertas guardadas" + filtros activos.
- Lista: #id, empresa, ubicación, fecha publicación (dd/mm/aaaa), chip nivel, fuente, título con link, botón 👁‍🗨 ocultar.
- Badge "Nueva" según timestamp de última visita (sección 4).
- Paginación: la web usa 20/página; en móvil se recomienda **scroll infinito** sobre la lista filtrada.
- Acciones de cabecera: ir a "Ocultas" y a "Buscar".

### 5.4 Ocultas
- Idéntica a Guardados pero listando `oculto=true`; el botón de acción restaura la oferta (toggle). Volver a Guardados desde aquí tras restaurar.

### 5.5 Comportamiento del toggle ocultar
- Al ocultar desde Guardados: la fila desaparece con animación de fade (~300ms) y el contador baja en 1. Sin recargar la lista completa.

---

## 6. Notas importantes

- **Credenciales**: la API requiere `email`/`password` (en Django viven en `.env` como `CVM_EMAIL`/`CVM_PASSWORD`). En la app deben configurarse vía variables de entorno de build (`react-native-config`, `expo-constants`). ⚠️ Embeber credenciales en una app distribuida es inseguro; para producción considerar un proxy/backend mínimo que haga login y reenvíe búsquedas.
- **Errores de red**: replicar la tolerancia de la web — si una página falla tras 3 reintentos, mostrar lo acumulado en vez de un error total. Errores de login (credenciales faltantes/inválidas) sí se muestran como error al usuario.
- **Zona horaria**: `x-client-data` y el filtro de periodos usan `America/Lima`.
- **Deduplicación**: siempre por `url` al agregar resultados de páginas múltiples, y por `api_id` al persistir localmente.
