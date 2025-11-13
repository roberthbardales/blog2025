"""
ASGI config for blog project.
Compatible con Daphne y Channels 4.0
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blog.settings')
django.setup()

# Imports después de setup
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from applications.chat.routing import websocket_urlpatterns

# Aplicación ASGI
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})

# Debug en consola
print("="*50)
print("✅ ASGI Application Loaded")
print(f"✅ WebSocket routes: {len(websocket_urlpatterns)} pattern(s)")
print("="*50)