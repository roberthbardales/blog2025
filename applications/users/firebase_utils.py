# applications/users/firebase_utils.py
import firebase_admin
from firebase_admin import credentials, auth as firebase_auth
from django.conf import settings

def init_firebase():
    if not firebase_admin._apps:
        cred_path = getattr(settings, "FIREBASE_CREDENTIALS", None)
        if not cred_path:
            raise RuntimeError("FIREBASE_CREDENTIALS no está configurado en settings.py")
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)

def verify_firebase_token(id_token):
    """
    Verifica el ID token con Firebase Admin y devuelve el token decodificado.
    Lanza firebase_admin.exceptions.* si falla.
    """
    init_firebase()
    decoded = firebase_auth.verify_id_token(id_token)
    return decoded
