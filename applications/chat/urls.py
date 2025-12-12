from django.urls import path
from . import views

urlpatterns = [
    path('ping/', views.ping, name='ping'),
    path('', views.ChatHomeView.as_view(), name='chat_home'),
    path('<int:user_id>/', views.ChatRoomView.as_view(), name='chat_room'),
    path('user-status/<int:user_id>/', views.user_status, name='user_status'),  # ← AGREGA ESTA LÍNEA
]
