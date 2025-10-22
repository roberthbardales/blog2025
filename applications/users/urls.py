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

    #Firebase URLs
    path(
        'login/google/',
        views.FirebaseGoogleLoginAPIView.as_view(),
        name='firebase-google-login'
    ),

    # path(
    #     'api/logout/',
    #     views.LogoutView.as_view(), name='logout'
    # ),
    # path('perfil2/',
    #      views.PerfilView.as_view(),
    #      name='perfil2'
    #      ),

]