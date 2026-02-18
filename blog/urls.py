"""
Proyecto Curso Django
"""
from django.contrib import admin
from django.urls import path, re_path, include

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path('', include('applications.users.urls')),
    # path('api/users/', include('users.urls')),
    re_path('', include('applications.home.urls')),
    re_path('', include('applications.entrada.urls')),
    #api
    re_path('api/', include('applications.entrada.api_urls')),

    re_path('', include('applications.favoritos.urls')),
    re_path('chat/', include('applications.chat.urls')),
    re_path('', include('applications.notas.urls')),
    # urls para ckeditor
    re_path(r'^ckeditor/', include('ckeditor_uploader.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
