# applications/users/backends.py
from django.contrib.auth import get_user_model
from firebase_admin import auth as firebase_auth
from django.contrib.auth.backends import BaseBackend

User = get_user_model()

class FirebaseBackend(BaseBackend):
    """Autenticación usando Firebase ID Token."""

    def authenticate(self, request, id_token=None, **kwargs):
        if not id_token:
            return None

        try:
            decoded_token = firebase_auth.verify_id_token(id_token)
            email = decoded_token.get("email")
            name = decoded_token.get("name", "")
            uid = decoded_token.get("uid")

            user, created = User.objects.get_or_create(
                email=email,
                defaults={"full_name": name or email.split("@")[0]}
            )
            return user
        except Exception as e:
            print("Error autenticando con Firebase:", e)
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
