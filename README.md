# 📝 Blog 2025

Plataforma de blog social construida con Django, que combina publicación de artículos con funcionalidades de red social: chat en tiempo real, sistema de amigos, favoritos, notas personales y autenticación con Firebase/Google.

---

## 📋 Descripción

Blog 2025 es una aplicación web completa que funciona como un **blog interactivo con elementos de red social**. Los usuarios pueden publicar artículos con editor enriquecido, interactuar a través de comentarios y likes, chatear en tiempo real con sus amigos, organizar entradas favoritas en grupos y gestionar notas personales con colores. El sistema incluye roles de usuario (Administrador / Usuario), geolocalización de visitantes y un widget de clima en tiempo real para Lima, Perú.

---

## 🛠️ Tecnologías

| Categoría | Tecnologías |
|---|---|
| **Backend** | Django 3.2, Django REST Framework, Django Channels 4.0 |
| **Frontend** | Bootstrap, jQuery, CKEditor (editor enriquecido) |
| **Base de datos** | PostgreSQL (con búsqueda trigram) |
| **Autenticación** | Django Auth (email/password), Firebase Auth (Google OAuth) |
| **Tiempo real** | WebSockets via Django Channels + Daphne |
| **API** | REST API con JWT (SimpleJWT) |
| **Geolocalización** | ipapi.co (IP → ubicación) |
| **Clima** | Open-Meteo API |
| **Almacenamiento** | Firebase Admin SDK (opcional) |
| **Utilidades** | django-model-utils, django-environ, Pillow (imágenes) |

---

## ✨ Principales Funcionalidades

### 📰 Blog / Entradas
- CRUD completo de entradas con editor CKEditor enriquecido
- Categorías y etiquetas (tags)
- Sistema de **likes** y **comentarios anidados** (hilos de respuesta)
- Entradas destacadas: portada, en página principal, recientes
- **Búsqueda difusa** con PostgreSQL trigram (similitud de texto)
- Perfil público de cada autor

### 👥 Red Social
- Sistema de **amigos** con solicitudes (enviar, aceptar, rechazar, cancelar)
- Bloqueo de usuarios
- Búsqueda de usuarios por nombre o email
- Perfil de red con estadísticas (amigos, publicaciones, solicitudes)

### 💬 Chat en Tiempo Real
- Chat privado uno-a-uno entre amigos vía **WebSockets**
- Indicador de presencia **online/offline** con ping cada 2 segundos
- Historial de mensajes almacenados en base de datos
- Marcaje automático de mensajes como leídos

### 🔖 Favoritos con Grupos
- Guardar entradas en **grupos de favoritos** personalizados
- Toggle rápido (agregar/quitar) desde la vista de detalle
- CRUD de grupos (crear, editar, eliminar)
- Mover entradas entre grupos
- Búsqueda y filtrado por grupo o categoría

### 📒 Notas Personales
- CRUD de notas adhesivas con **6 colores** (amarillo, azul, verde, rosa, naranja, morado)
- Marcado de importancia (las importantes aparecen primero)

### 🔐 Autenticación y Roles
- Registro e inicio de sesión con **email y contraseña**
- Login con **Google** vía Firebase Auth
- Roles: **Administrador** (CRUD entradas, gestionar categorías, ver analytics) y **Usuario** (leer, comentar, chatear)
- REST API protegida con **JWT** (SimpleJWT)

### 📊 Analytics y Geolocalización
- Registro de visitas con IP, ubicación, user-agent y ruta visitada
- Dashboard de analytics (solo admin): visitas totales, IPs únicas, ciudades, países
- Geolocalización vía ipapi.co con caché de 24 horas

### 🌤️ Extras
- Widget de clima en tiempo real para Lima (Open-Meteo API, caché 30 min)
- Formulario de contacto y suscripción por email
- Barra lateral con contenido dinámico
- Widget de WhatsApp flotante

---

## 📁 Estructura del Proyecto

```
blog2025/
├── manage.py                    # Comando de gestión de Django
├── requirements.txt             # Dependencias de Python
├── .env                         # Variables de entorno (no commitear)
├── .gitignore
├── firebase-key.json            # Credenciales Firebase (no commitear)
│
├── blog/                        # Configuración del proyecto Django
│   ├── settings.py              # Configuración principal
│   ├── urls.py                  # Enrutador principal
│   ├── asgi.py                  # Configuración ASGI (WebSockets)
│   └── wsgi.py                  # Configuración WSGI
│
├── applications/                # Aplicaciones Django
│   ├── processors.py            # Context processors (clima, IP, contactos)
│   ├── home/                    # Landing page, sobre mí, portafolio, analytics
│   ├── users/                   # Autenticación, registro, perfil, API de usuarios
│   ├── entrada/                 # Entradas del blog, categorías, tags, likes, comentarios, API
│   ├── favoritos/               # Sistema de favoritos con grupos
│   ├── amigos/                  # Red social: solicitudes, bloqueo, perfil de red
│   ├── chat/                    # Chat en tiempo real con WebSockets
│   ├── notas/                   # Notas personales con colores
│   └── Notificaciones/         # (Placeholders para futuro)
│
├── templates/                   # Templates HTML
│   ├── base.html                # Plantilla base principal
│   ├── layout_sidebar.html      # Layout con barra lateral
│   ├── includes/                # Header, footer, sidebar, widgets
│   ├── home/                    # Landing, sobre mí, portafolio
│   ├── users/                   # Login, registro, perfil
│   ├── entrada/                 # Lista, detalle, CRUD de entradas
│   ├── favoritos/               # Perfil de favoritos, grupos
│   ├── amigos/                  # Lista de amigos, búsqueda
│   ├── chat/                    # Home y sala de chat
│   └── notas/                   # CRUD de notas
│
├── static/                      # Archivos estáticos
│   ├── css/                     # Hojas de estilo
│   ├── js/                      # JavaScript (jQuery, Bootstrap, efectos)
│   └── img/                     # Imágenes, logos, favicon
│
└── media/                       # Archivos subidos por usuarios
    └── avatars/                 # Avatares de usuario
```

---

## 📦 Requisitos

- **Python** 3.9+
- **PostgreSQL** 12+
- **Node.js** (opcional, para herramientas de frontend)
- Cuenta de **Firebase** con Authentication habilitada (para login con Google)
- API key de **Google** (para geolocalización IP, opcional)

---

## 🚀 Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/blog2025.git
cd blog2025
```

### 2. Crear entorno virtual

```bash
python -m venv env_blog2025

# Windows
env_blog2025\Scripts\activate

# Linux / macOS
source env_blog2025/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:

```env
# Django
SECRET_KEY=tu-clave-secreta-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Base de datos PostgreSQL
DB_NAME=nombre_de_tu_base
DB_USER=usuario_de_postgres
DB_PASSWORD=tu_password
DB_HOST=localhost
DB_PORT=5432

# Email (SMTP - Gmail)
EMAIL_HOST_USER=tu-correo@gmail.com
EMAIL_HOST_PASSWORD=tu-app-password-de-gmail

# Firebase (autenticación con Google)
FIREBASE_KEY_PATH=firebase-key.json
FIREBASE_API_KEY=tu-firebase-api-key
FIREBASE_AUTH_DOMAIN=tu-proyecto.firebaseapp.com
FIREBASE_PROJECT_ID=tu-proyecto-id
FIREBASE_MESSAGING_SENDER_ID=tu-sender-id
FIREBASE_APP_ID=tu-app-id

# Gemini AI (opcional)
GEMINI_API_KEY=tu-api-key
GEMINI_MODEL=gemini-2.5-flash
```

### 5. Configurar Firebase

1. Crea un proyecto en [Firebase Console](https://console.firebase.google.com/)
2. Habilita **Authentication** → método **Google**
3. Descarga el archivo de credenciales JSON (SDK Admin)
4. Renómbralo a `firebase-key.json` y colócalo en la raíz del proyecto

### 6. Crear la base de datos

```bash
# En PostgreSQL
psql -U postgres
CREATE DATABASE db_blog2025;
CREATE USER tu_usuario WITH PASSWORD 'tu_password';
ALTER ROLE tu_usuario SET client_encoding TO 'utf8';
ALTER ROLE tu_usuario SET default_transaction_isolation TO 'read committed';
ALTER ROLE tu_usuario SET timezone TO 'America/Lima';
GRANT ALL PRIVILEGES ON DATABASE db_blog2025 TO tu_usuario;
\q
```

### 7. Ejecutar migraciones

```bash
python manage.py migrate
```

### 8. Crear superusuario

```bash
python manage.py createsuperuser
```

---

## ⚡ Ejecutar en Desarrollo

```bash
# Activar entorno virtual
env_blog2025\Scripts\activate   # Windows
# source env_blog2025/bin/activate   # Linux/macOS

# Ejecutar servidor con soporte WebSocket (Daphne)
python manage.py runserver 8000
```

> **Nota:** El servidor usa **Daphne** (ASGI) para soporte de WebSockets. Al ejecutar `runserver`, Django Channels maneja tanto HTTP como WebSocket automáticamente.

### Windows (atajo)

Doble clic en `activar blog.bat` para iniciar el servidor directamente en el puerto **8000**.

Accede a: [http://localhost:8000](http://localhost:8000)

---

## 🌐 Desplegar en Producción

### Requisitos del servidor

- Python 3.9+ en el servidor
- PostgreSQL configurado
- Nginx o Apache como reverse proxy
- SSL/HTTPS (necesario para WebSockets en producción)

### Pasos

```bash
# 1. Configurar .env con valores de producción
DEBUG=False
ALLOWED_HOSTS=tu-dominio.com

# 2. Recolectar archivos estáticos
python manage.py collectstatic

# 3. Ejecutar migraciones
python manage.py migrate

# 4. Configurar Daphne (ASGI) con systemd
daphne -b 0.0.0.0 -p 8000 blog.asgi:application
```

### Ejemplo de servicio systemd

```ini
# /etc/systemd/system/blog2025.service
[Unit]
Description=Blog 2025 ASGI Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/ruta/al/proyecto
ExecStart=/ruta/al/venv/bin/daphne -b 0.0.0.0 -p 8000 blog.asgi:application

[Install]
WantedBy=multi-user.target
```

### Configuración de Nginx (ejemplo)

```nginx
server {
    listen 80;
    server_name tu-dominio.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name tu-dominio.com;

    ssl_certificate /ruta/cert.pem;
    ssl_certificate_key /ruta/key.pem;

    location /static/ {
        alias /ruta/al/proyecto/staticfiles/;
    }

    location /media/ {
        alias /ruta/al/proyecto/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Producción: Channel Layers

Para producción, cambia en `settings.py` el `CHANNEL_LAYERS` a Redis:

```python
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {"hosts": [("127.0.0.1", 6379)]},
    },
}
```

---

## 🔑 Variables de Entorno

| Variable | Descripción | Requerida |
|---|---|---|
| `SECRET_KEY` | Clave secreta de Django | ✅ Sí |
| `DEBUG` | Modo debug (`True`/`False`) | ✅ Sí |
| `ALLOWED_HOSTS` | Hosts permitidos (separados por coma) | ✅ Sí |
| `DB_NAME` | Nombre de la base de datos PostgreSQL | ✅ Sí |
| `DB_USER` | Usuario de PostgreSQL | ✅ Sí |
| `DB_PASSWORD` | Contraseña de PostgreSQL | ✅ Sí |
| `DB_HOST` | Host de PostgreSQL (default: `localhost`) | ❌ No |
| `DB_PORT` | Puerto de PostgreSQL (default: `5432`) | ❌ No |
| `EMAIL_HOST_USER` | Correo SMTP para envío de emails | ✅ Sí |
| `EMAIL_HOST_PASSWORD` | Contraseña/app password del correo SMTP | ✅ Sí |
| `FIREBASE_KEY_PATH` | Ruta al archivo JSON de credenciales Firebase | ✅ Sí |
| `FIREBASE_API_KEY` | API Key de Firebase | ✅ Sí |
| `FIREBASE_AUTH_DOMAIN` | Dominio de autenticación Firebase | ✅ Sí |
| `FIREBASE_PROJECT_ID` | ID del proyecto Firebase | ✅ Sí |
| `FIREBASE_MESSAGING_SENDER_ID` | ID del remitente Firebase | ✅ Sí |
| `FIREBASE_APP_ID` | ID de la aplicación Firebase | ✅ Sí |
| `GEMINI_API_KEY` | API Key de Google Gemini (para IA) | ❌ No |
| `GEMINI_MODEL` | Modelo de Gemini (default: `gemini-2.5-flash`) | ❌ No |

---

## 📡 API Endpoints

### Autenticación JWT

| Método | Endpoint | Descripción |
|---|---|---|
| `POST` | `/api/token/` | Obtener token de acceso |
| `POST` | `/api/token/refresh/` | Refrescar token |

### Usuarios

| Método | Endpoint | Auth | Descripción |
|---|---|---|---|
| `POST` | `/api/users/register/` | No | Registrar usuario |
| `GET/PUT/PATCH` | `/api/users/perfil/` | Sí | Ver/editar perfil |
| `GET` | `/api/users/lista/` | Admin | Listar usuarios |
| `GET` | `/api/users/sobre_mi/` | Sí | Info del usuario actual |

### Entradas

| Método | Endpoint | Auth | Descripción |
|---|---|---|---|
| `GET` | `/api/entries/entries/` | No | Listar entradas |
| `POST` | `/api/entries/entries/create/` | Sí | Crear entrada |
| `GET` | `/api/entries/entries/<slug>/` | No | Detalle de entrada |

---

## 🧪 Estructura de Base de Datos

| Modelo | App | Descripción |
|---|---|---|
| `User` | users | Modelo de usuario personalizado (email como USERNAME_FIELD) |
| `Entry` | entrada | Entradas del blog con CKEditor |
| `Category` | entrada | Categorías de entradas |
| `Tag` | entrada | Etiquetas de entradas |
| `Comment` | entrada | Comentarios con soporte de hilos anidados |
| `Like` | entrada | Likes de usuarios en entradas |
| `Favorites` | favoritos | Entradas guardadas como favoritas |
| `FavoriteGroup` | favoritos | Grupos de favoritos |
| `Friendship` | amigos | Relaciones de amistad con estados |
| `Message` | chat | Mensajes del chat |
| `UserStatus` | chat | Estado de presencia online/offline |
| `Nota` | notas | Notas personales con colores |
| `Home` | home | Configuración CMS de la landing |
| `Suscribers` | home | Suscriptores del blog |
| `Contact` | home | Mensajes de contacto |
| `IPLocation` | home | Geolocalización de IPs |
| `VisitorLog` | home | Registro de visitas |

---

## 🔒 Permisos y Roles

| Rol | Código | Capacidades |
|---|---|---|
| **Superuser** | `is_superuser=True` | Acceso total + panel admin Django |
| **Administrador** | `ocupation='0'` | Crear/editar/eliminar entradas, gestionar categorías, ver analytics de visitas |
| **Usuario** | `ocupation='1'` | Leer entradas, comentar, dar like, favoritos, chat, notas, solicitudes de amistad |
| **Otro** | `ocupation='2'` | Acceso limitado |

---

## 📄 Licencia

Este proyecto está bajo la licencia **MIT**. Consulta el archivo [LICENSE](LICENSE) para más detalles.

---

## 👨‍💻 Autor

**Robert Bardales** — Desarrollador Full Stack

- 📧 Email: roberthbardales@gmail.com
- 🔗 GitHub: [github.com/tu-usuario](https://github.com/tu-usuario)
- 💼 LinkedIn: [linkedin.com/in/tu-usuario](https://linkedin.com/in/tu-usuario)

---

> Desarrollado con ❤️ usando Django, PostgreSQL y Firebase
