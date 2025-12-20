# applications/chat/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Vista principal del chat
    path('', views.ChatHomeView.as_view(), name='chat_home'),

    # Sala de chat con usuario específico
    path('<int:user_id>/', views.ChatRoomView.as_view(), name='chat_room'),

    # Endpoints de estado
    path('ping/', views.ping, name='ping'),
    path('user-status/<int:user_id>/', views.user_status, name='user_status'),
    path('bulk-user-status/', views.bulk_user_status, name='bulk_user_status'),
]