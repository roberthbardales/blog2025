# applications/users/backends.py
from django.contrib.auth import get_user_model
from .firebase_utils import verify_firebase_token

User = get_user_model()

class FirebaseAuthenticationBackend:
    """
    Permite llamar authenticate(request, token=idToken) y devolver User.
    """
    def authenticate(self, request, token=None):
        if not token:
            return None
        try:
            decoded = verify_firebase_token(token)
        except Exception:
            return None

        uid = decoded.get('uid')
        email = decoded.get('email')
        if not uid or not email:
            return None

        # Buscar por firebase_uid
        try:
            return User.objects.get(firebase_uid=uid)
        except User.DoesNotExist:
            pass

        # Buscar por email y asociar
        try:
            user = User.objects.get(email__iexact=email)
            user.firebase_uid = uid
            user.save()
            return user
        except User.DoesNotExist:
            # Crear nuevo usuario
            username = f"{email.split('@')[0]}_{uid[:6]}"
            user = User.objects.create(
                username=username,
                email=email,
                firebase_uid=uid,
                is_active=True,
            )
            user.set_unusable_password()
            user.save()
            return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
