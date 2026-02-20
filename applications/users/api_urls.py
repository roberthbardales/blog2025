from django.urls import path
from .api_views import (        # ← api_views, no views
    UserRegisterAPIView,
    UserProfileAPIView,
    UserListAPIView,
)
from .views import SobreMiAPIView

app_name = 'users_api'

urlpatterns = [
    path('register/', UserRegisterAPIView.as_view(), name='api-register'),
    path('perfil/', UserProfileAPIView.as_view(), name='api-perfil'),
    path('lista/', UserListAPIView.as_view(), name='api-lista-usuarios'),
    path('sobre_mi/', SobreMiAPIView.as_view(), name='api-sobre-mi'),
]