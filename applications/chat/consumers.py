# applications/chat/consumers.py CORREGIDO
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Message

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Conexión del WebSocket"""
        self.other_user_id = self.scope['url_route']['kwargs']['user_id']
        self.user = self.scope["user"]

        # Verificar autenticación
        if not self.user.is_authenticated:
            await self.close()
            return

        # Crear nombre de sala único para ambos usuarios
        # Ordenamos los IDs para que siempre sea el mismo nombre de sala
        user_ids = sorted([self.user.id, int(self.other_user_id)])
        self.room_name = f"chat_{user_ids[0]}_{user_ids[1]}"
        self.room_group_name = self.room_name

        # Unirse al grupo de la sala
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Aceptar la conexión
        await self.accept()

        print(f"✅ Usuario {self.user.id} conectado a sala: {self.room_name}")

    async def disconnect(self, close_code):
        """Desconexión del WebSocket"""
        # Salir del grupo de la sala
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print(f"❌ Usuario desconectado de sala: {self.room_name}")

    async def receive(self, text_data):
        """Recibir mensaje del WebSocket"""
        try:
            data = json.loads(text_data)
            message = data.get("message", "").strip()

            if not message:
                return

            sender = self.user
            receiver = await self.get_user_by_id(self.other_user_id)

            # Guardar mensaje en la base de datos
            await self.save_message(sender, receiver, message)

            # Enviar mensaje al grupo
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": message,
                    "sender_id": sender.id,
                    "sender_name": sender.get_full_name()
                }
            )

            print(f"📨 Mensaje de {sender.id} a {receiver.id}: {message[:50]}")

        except Exception as e:
            print(f"❌ Error en receive: {e}")

    async def chat_message(self, event):
        """Enviar mensaje al WebSocket"""
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "sender_id": event["sender_id"],
            "sender_name": event["sender_name"]
        }))

    @database_sync_to_async
    def get_user_by_id(self, user_id):
        """Obtener usuario por ID"""
        return User.objects.get(id=user_id)

    @database_sync_to_async
    def save_message(self, sender, receiver, content):
        """Guardar mensaje en la base de datos"""
        return Message.objects.create(
            sender=sender,
            recipient=receiver,
            content=content
        )