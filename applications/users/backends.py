from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class FirebaseBackend(ModelBackend):
    """
    Autenticador personalizado para usuarios que inician sesión con Firebase.
    """
    def authenticate(self, request, firebase_uid=None, **kwargs):
        if firebase_uid is None:
            return None
        try:
            return User.objects.get(firebase_uid=firebase_uid)
        except User.DoesNotExist:
            return None
