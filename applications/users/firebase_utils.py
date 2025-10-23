import firebase_admin
from firebase_admin import auth, credentials
from django.conf import settings

# Inicializar Firebase solo una vez
if not firebase_admin._apps:
    cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS)
    firebase_admin.initialize_app(cred)

def verify_firebase_token(id_token):
    """
    Verifica y decodifica el token de Firebase.
    Retorna el payload con email, uid, name, etc.
    Lanza excepción si el token no es válido o expiró.
    """
    decoded = auth.verify_id_token(id_token)
    return decoded
