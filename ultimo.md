# Cómo configurar los filtros de empleo

El sistema ya está funcionando: recibe empleos por **email** y **Telegram** automáticamente (cron cada hora), buscando con los filtros que definas.

## Dónde configurar los filtros de empleo

### Opción 1: Página web (recomendada)
- Logueado en el blog: **Empleos → Filtros**
- URL: `http://tudominio/empleos/filtros/`
- Ves la lista de filtros. El de prueba es **"Backend Python"**.
- Pulsa el **icono de lápiz** (editar) para modificar qué empleos te llegan.

### Opción 2: Django admin
- `/admin/` → sección **Empleos → Filtros de empleo**.

## Qué campos puedes ajustar para filtrar lo que te llega

| Campo | Qué controla | Ejemplo |
|---|---|---|
| **Palabras clave** | La tecnología/puesto que buscas (obligatorio) | `python, django, linux` |
| **País** | Perú, México, Colombia, Chile, Argentina, España | Perú |
| **Antigüedad** | Qué tan recientes (último día, 3 días, semana, mes) | Última semana |
| **Nivel (seniority)** | Prácticas / Junior / Semi Senior / Senior | Junior + Semi Senior |
| **Modalidad/Categoría/Tipo (IDs)** | IDs específicos de la API (avanzado, opcional) | — |
| **Salario mín/máx + moneda** | Rango salarial | 3000 – 8000 soles |
| **¿Inglés?** | Requisito de inglés (Sí/No/—) | — |
| **Email / Telegram** | Destino (vacío = usa los del `.env`) | vacío |
| **Activo** | Si el filtro se ejecuta o no | marcado |

## Ejemplo del flujo para afinar
1. Entra a **Empleos → Filtros** → editar **"Backend Python"**.
2. Cambia las **palabras clave** a lo que quieras (ej. solo `django`), deja el **país**, ajusta **antigüedad**/**nivel**/**salario**.
3. Guarda. Cada hora el cron notificará los empleos nuevos que cumplan **solo ese filtro**.
4. Puedes crear varios filtros (cada uno es una "receta" independiente).

## Nota importante — demasiadas ofertas
Con `python` solo en 7 días hay ~243 ofertas en Perú: es **demasiado amplio** y te llegará mucho. Para no saturar tu Telegram, conviene filtrar más:
- Reducir a keywords específicas (ej. `django` → 2 ofertas).
- Subir el salario mínimo.
- Limitar a 1 día de antigüedad.
