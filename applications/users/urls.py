#
from django.urls import path
from .views import FirebaseLoginView
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
    path('login/firebase/', views.FirebaseLoginView.as_view(), name='firebase-login'),

    path("login/google/", views.login_google_view, name="google-login-template"),

    path("login/firebase-datos/", views.firebase_datos_view, name="firebase-datos"),


    #pruebas API
    path('api/sobre_mi/', views.SobreMiAPIView.as_view(), name='api-sobre-mi'),

]
