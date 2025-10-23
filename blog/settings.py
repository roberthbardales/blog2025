# from django.core.exceptions import ImproperlyConfigured
# import json
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


from pathlib import Path
import firebase_admin
from firebase_admin import credentials
from unipath import Path as UniPath



# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = UniPath(__file__).ancestor(2)
# BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# with open("secret.json") as f:
#     secret = json.loads(f.read())

# def get_secret(secret_name, secrets=secret):
#     try:
#         return secrets[secret_name]
#     except:
#         msg = "la variable %s no existe" % secret_name
#         raise ImproperlyConfigured(msg)

SECRET_KEY = '^cv997**%ht!&!+qunlefo#2i&7#tfn-9#1d5_253hhi8516#f'
# Para debug de carga:
# print("SECRET_KEY cargada:", SECRET_KEY)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
ALLOWED_HOSTS = []

# Application definition
DJANGO_APPS = (
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
)

THIRD_PARTY_APPS = (
    'ckeditor',
    'ckeditor_uploader',
    'rest_framework',
    # 'import_export',
    # 'django_quill',
)

# 🔧 IMPORTANTE: suma tuplas, no listas
INSTALLED_APPS = DJANGO_APPS + LOCAL_APPS + THIRD_PARTY_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'blog.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'blog.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'db_blog2025',
        'USER': 'russell',
        'PASSWORD': 'russell2020',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTH_USER_MODEL = 'users.User'

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/Lima'
# TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Static and Media files
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR.child('static')]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR.child('media')

# CKEDITOR SETTINGS
CKEDITOR_UPLOAD_PATH = 'uploads/'
CKEDITOR_IMAGE_BACKEND = 'pillow'
CKEDITOR_JQUERY_URL = 'https://ajax.googleapis.com/ajax/libs/jquery/2.2.4/jquery.min.js'

CKEDITOR_CONFIGS = {
    'default': {
        'width': 'full',
        'height': '350',
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
        'height': '350',
        'toolbar_Special': [
            ['Bold', 'Italic', 'Underline'],
            ['NumberedList', 'BulletedList', '-', 'OutIdent', 'Ident', '-', 'JustifyLeft', 'JustifyRight', 'JustifyCenter'],
            ['TextColor', 'Format', 'FontSize', 'Link'],
            ['Image', 'Smiley', 'Iframe'],
            ['RemoveFormat', 'Source'],
            ['CodeSnippet'],
        ],
        'extraPlugins': 'codesnippet',
    }
}


# Email configuration
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "roberthbardales@gmail.com"
EMAIL_HOST_PASSWORD = "uoqynxrrhwfcdtli"
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER


# Ruta al JSON de la cuenta de servicio Firebase (no lo subas al repo)
FIREBASE_CREDENTIALS = os.path.join(BASE_DIR, 'serviceAccountKey.json')

# Backends: agrega el backend de Firebase antes del backend por defecto (opcional)
AUTHENTICATION_BACKENDS = [
    'applications.users.backends.FirebaseAuthenticationBackend',
    'django.contrib.auth.backends.ModelBackend',
]

