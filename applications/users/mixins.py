from django.urls import reverse_lazy, reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.views.generic import View
#
from .models import User

#DRF API imports

from rest_framework.permissions import BasePermission, IsAuthenticated
from django.contrib.auth import get_user_model

def check_ocupation_user(ocupation, user_ocupation):
    #

    if (ocupation == User.ADMINISTRADOR or ocupation == user_ocupation):

        return True
    else:
        return False

class AdministradorPermisoMixin(LoginRequiredMixin):
    login_url = reverse_lazy('users_app:user-login')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        #
        if not check_ocupation_user(request.user.ocupation, User.ADMINISTRADOR):
            # no tiene autorizacion
            return HttpResponseRedirect(
                reverse(
                    'users_app:user-login'
                )
            )

        return super().dispatch(request, *args, **kwargs)

class UsuarioPermisoMixin(LoginRequiredMixin):
    login_url = reverse_lazy('users_app:user-login')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        #
        if not check_ocupation_user(request.user.ocupation, User.USUARIO):
            # no tiene autorizacion
            return HttpResponseRedirect(
                reverse(
                    'users_app:user-login'
                )
            )

        return super().dispatch(request, *args, **kwargs)

#Permisos API permissions

User = get_user_model()

# 🔐 Permiso base
class RolPermission(BasePermission):
    """Valida que el usuario tenga un rol específico (ocupation)."""
    rol = None

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and str(request.user.ocupation) == str(self.rol)
        )

# 🧱 Mixins para vistas API
class AdministradorAPIMixin:
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        from .mixins import RolPermission
        permiso = RolPermission()
        permiso.rol = User.ADMINISTRADOR
        return [permiso()]

class UsuarioAPIMixin:
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        from .mixins import RolPermission
        permiso = RolPermission()
        permiso.rol = User.USUARIO
        return [permiso()]





# class UsuarioPermisoMixin(LoginRequiredMixin):
#     login_url = reverse_lazy('users_app:user-login')

#     def dispatch(self, request, *args, **kwargs):
#         if not request.user.is_authenticated:
#             return self.handle_no_permission()
#         #
#         if not check_ocupation_user(request.user.ocupation, User.ALMACEN):
#             # no tiene autorizacion
#             return HttpResponseRedirect(
#                 reverse(
#                     'users_app:user-login'
#                 )
#             )

#         return super().dispatch(request, *args, **kwargs)
