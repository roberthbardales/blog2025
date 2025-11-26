# permissions.py
from rest_framework.permissions import BasePermission
from .models import User

def check_ocupation_user(user, required_ocupation):
    """
    Retorna True si el usuario es administrador o su ocupation coincide con la requerida.
    """
    if not user or not user.is_authenticated:
        return False

    # Administrador siempre tiene acceso
    if str(user.ocupation) == str(User.ADMINISTRADOR):
        return True

    # Coincide con la ocupation requerida
    return str(user.ocupation) == str(required_ocupation)


class EsUsuario(BasePermission):
    """
    Permite acceso solo si el usuario está autenticado y su ocupation es USUARIO,
    o si es administrador.
    """
    def has_permission(self, request, view):
        return check_ocupation_user(request.user, User.USUARIO)


class EsAdministrador(BasePermission):
    """
    Permite acceso solo si el usuario está autenticado y su ocupation es ADMINISTRADOR.
    """
    def has_permission(self, request, view):
        return check_ocupation_user(request.user, User.ADMINISTRADOR)
