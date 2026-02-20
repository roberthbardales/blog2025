
from django.contrib import admin
from django.urls import path, re_path, include

from django.conf import settings
from django.conf.urls.static import static
# jwt para apis
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    path('admin/', admin.site.urls),

    # Apps con vistas normales
    re_path('', include('applications.users.urls')),
    re_path('', include('applications.home.urls')),
    re_path('', include('applications.entrada.urls')),
    re_path('', include('applications.favoritos.urls')),
    re_path('chat/', include('applications.chat.urls')),
    re_path('', include('applications.notas.urls')),

    # APIs
    path('api/entries/', include('applications.entrada.api_urls')),
    path('api/users/', include('applications.users.api_urls')),

    # JWT tokens
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # CKEditor
    re_path(r'^ckeditor/', include('ckeditor_uploader.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)