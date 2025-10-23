from rest_framework import serializers
from django.contrib.auth import get_user_model
from .firebase_utils import verify_firebase_token
from django.core.exceptions import ObjectDoesNotExist

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'nombres', 'apellidos')

class FirebaseAuthSerializer(serializers.Serializer):
    idToken = serializers.CharField(write_only=True)

    def validate_idToken(self, value):
        try:
            decoded = verify_firebase_token(value)
        except Exception:
            raise serializers.ValidationError("Token inválido o expirado.")

        email = decoded.get('email')
        uid = decoded.get('uid')
        if not email or not uid:
            raise serializers.ValidationError("Token no contiene email o uid válido.")
        self.context['firebase_decoded'] = decoded
        return value

    def create_or_get_user(self):
        decoded = self.context.get('firebase_decoded')
        if not decoded:
            raise RuntimeError("Token verificado no encontrado en contexto.")

        email = decoded.get('email')
        uid = decoded.get('uid')
        name = decoded.get('name', '')
        first_name, last_name = '', ''
        if name:
            parts = name.split(' ', 1)
            first_name = parts[0]
            if len(parts) > 1:
                last_name = parts[1]

        # 1) Buscar por firebase_uid
        try:
            user = User.objects.get(firebase_uid=uid)
            return user
        except ObjectDoesNotExist:
            pass

        # 2) Buscar por email
        try:
            user = User.objects.get(email__iexact=email)
            user.firebase_uid = uid
            if not getattr(user, 'nombres', None) and first_name:
                user.nombres = first_name
            if not getattr(user, 'apellidos', None) and last_name:
                user.apellidos = last_name
            user.save()
            return user
        except ObjectDoesNotExist:
            pass

        # 3) Crear nuevo usuario
        username_base = email.split('@')[0]
        username = f"{username_base}_{uid[:6]}"
        user = User.objects.create(
            username=username,
            email=email,
            nombres=first_name,
            apellidos=last_name,
            firebase_uid=uid,
            is_active=True
        )
        user.set_unusable_password()
        user.save()
        return user
