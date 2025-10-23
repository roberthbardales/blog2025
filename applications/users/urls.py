#
from django.urls import path

from . import views

app_name = "users_app"

urlpatterns = [
    path(
        'register/',
        views.UserRegisterView.as_view(),
        name='user-register',
    ),
    path(
        'login/',
        views.LoginUser.as_view(),
        name='user-login',
    ),
    path(
        'logout/',
        views.LogoutView.as_view(),
        name='user-logout',
    ),
    path(
        'update/',
        views.UpdatePasswordView.as_view(),
        name='user-update',
    ),
        path(
        'users/lista/',
        views.UserListView.as_view(),
        name='user-lista',
    ),

    # Firebase login
    path('login/firebase/', views.FirebaseLoginAPIView.as_view(), name='firebase-login'),
    path('api/firebase-login/', views.FirebaseLoginAPI.as_view(), name='api_firebase_login'),
]
