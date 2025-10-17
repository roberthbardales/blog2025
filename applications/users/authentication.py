from rest_framework import authentication, exceptions
from firebase_admin import auth as firebase_auth
from django.contrib.auth import get_user_model

User = get_user_model()

class FirebaseAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return None

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            raise exceptions.AuthenticationFailed('Invalid Authorization header')

        token = parts[1]
        try:
            decoded = firebase_auth.verify_id_token(token)
        except Exception:
            raise exceptions.AuthenticationFailed('Invalid or expired token')

        uid = decoded.get('uid')
        email = decoded.get('email')
        user, created = User.objects.get_or_create(
            email=email or f"{uid}@firebase.local",
            defaults={'full_name': email or 'Firebase User'}
        )
        return (user, None)
