import os
import environ
from unipath import Path as UniPath
import firebase_admin
from firebase_admin import credentials

# -------------------------------
# BASE_DIR
# -------------------------------
BASE_DIR = UniPath(__file__).ancestor(2)

# -------------------------------
# django-environ
# -------------------------------
env = environ.Env(
    DEBUG=(bool, False)
)
# Cargar archivo .env (solo si existe)
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# -------------------------------
# SECRET_KEY & DEBUG
# -------------------------------
SECRET_KEY = env('SECRET_KEY')
DEBUG = env.bool('DEBUG')

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])

# -------------------------------
# INSTALLED_APPS
# -------------------------------
DJANGO_APPS = (
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',
)

LOCAL_APPS = (
    'applications.users',
    'applications.home',
    'applications.entrada',
    'applications.favoritos',
    'applications.chat',
    'applications.notas',
)

THIRD_PARTY_APPS = (
    'ckeditor',
    'ckeditor_uploader',
    'rest_framework',
    'channels',
)

INSTALLED_APPS = DJANGO_APPS + LOCAL_APPS + THIRD_PARTY_APPS

# -------------------------------
# MIDDLEWARE
# -------------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'applications.home.middleware.VisitorLogMiddleware',    # Middleware personalizado para logging de visitas
]

ROOT_URLCONF = 'blog.urls'

# -------------------------------
# TEMPLATES
# -------------------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR.child('templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'applications.procesors.home_contact',
                'applications.procesors.obtener_ip',
                'applications.procesors.obtener_clima',
            ],
        },
    },
]

# -------------------------------
# WSGI & ASGI
# -------------------------------
WSGI_APPLICATION = 'blog.wsgi.application'
ASGI_APPLICATION = 'blog.asgi.application'

# -------------------------------
# Channels (desarrollo: InMemory, prod: Redis)
# -------------------------------
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}

# -------------------------------
# DATABASES
# -------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST', default='localhost'),
        'PORT': env('DB_PORT', default='5432'),
    }
}

# -------------------------------
# Password validation
# -------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

AUTH_USER_MODEL = 'users.User'

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/chat/'

# -------------------------------
# Internationalization
# -------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/Lima'
USE_I18N = True
USE_L10N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# -------------------------------
# Static and Media
# -------------------------------
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR.child('static')]
STATIC_ROOT = BASE_DIR.child('staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR.child('media')

# -------------------------------
# CKEDITOR
# -------------------------------
CKEDITOR_UPLOAD_PATH = 'uploads/'
CKEDITOR_IMAGE_BACKEND = 'pillow'
CKEDITOR_JQUERY_URL = 'https://ajax.googleapis.com/ajax/libs/jquery/2.2.4/jquery.min.js'

CKEDITOR_CONFIGS = {
    'default': {
        'width': 'full',
        'height': '250',
        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Bold', 'Italic', 'Underline'],
            ['NumberedList', 'BulletedList', '-', 'OutIdent', 'Ident', '-', 'JustifyLeft', 'JustifyRight', 'JustifyCenter'],
            ['TextColor', 'Format', 'FontSize', 'Link'],
            ['Image', 'Smiley', 'Iframe'],
            ['RemoveFormat', 'Source'],
        ],
        'stylesSet': [],
    },
    'special': {
        'toolbar': 'Special',
        'width': '100%',
        'height': '450',
        'toolbar_Special': [
            ['Bold', 'Italic', 'Underline'],
            ['NumberedList', 'BulletedList', '-', 'OutIdent', 'Ident', '-', 'JustifyLeft', 'JustifyRight', 'JustifyCenter'],
            ['TextColor', 'Format', 'FontSize', 'Link'],
            # ['Image', 'Smiley', 'Iframe',],
            ['Image', 'Iframe',],
            ['RemoveFormat', 'Source'],
            ['CodeSnippet', 'QuickCode'],  # ← Agrega 'QuickCode' aquí
        ],
        'extraPlugins': 'codesnippet',
        'codeSnippet_theme': 'monokai',  # Añade esto para mejor visualización
        'codeSnippet_languages': {
            'python': 'Python',
            'javascript': 'JavaScript',
            'html': 'HTML',
            'css': 'CSS',
            'java': 'Java',
            'php': 'PHP',
            'sql': 'SQL',
            'bash': 'Bash',
        },
    }
}
# -------------------------------
# Email
# -------------------------------
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# -------------------------------
# Firebase
# -------------------------------
cred_path = env('FIREBASE_KEY_PATH')
cred = credentials.Certificate(BASE_DIR.child(cred_path))
firebase_admin.initialize_app(cred)
FIREBASE_CREDENTIALS = BASE_DIR.child(cred_path)

# -------------------------------
# Authentication Backends
# -------------------------------
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'applications.users.backends.FirebaseBackend',
]
