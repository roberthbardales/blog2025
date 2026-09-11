# applications/chat/consumers.py CORREGIDO
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Message
from applications.notificaciones.models import Notification
from applications.notificaciones.services import crear_notificacion

User = get_user_model()

UNREAD_LIMIT = 60  # caracteres del preview de notificación

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

            # Notificar al receptor vía su canal personal de notificaciones
            if sender.id != receiver.id:
                preview = message[:UNREAD_LIMIT]
                await self.crear_notificacion_db(
                    sender,
                    receiver,
                    Notification.KIND_MESSAGE,
                    f"{sender.get_full_name()}: {preview}",
                    f"/chat/{sender.id}/",
                )
                await self.channel_layer.group_send(
                    f"user_{receiver.id}",
                    {
                        "type": "notification_message",
                        "kind": Notification.KIND_MESSAGE,
                        "sender_id": sender.id,
                        "sender_name": sender.get_full_name(),
                        "preview": preview,
                        "room_url": f"/chat/{sender.id}/",
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

        # Si soy el receptor y estoy viendo la sala, marco como leído y
        # refresco el contador global de notificaciones del header.
        if self.user.id != event["sender_id"]:
            await self.mark_messages_read(event["sender_id"])
            total = await self.get_unread_count()
            await self.channel_layer.group_send(
                f"user_{self.user.id}",
                {"type": "badge_update", "total": total},
            )

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

    @database_sync_to_async
    def crear_notificacion_db(self, actor, recipient, kind, text, url=''):
        """Persistir y emitir la notificación fuera del event loop."""
        return crear_notificacion(actor, recipient, kind, text, url)

    @database_sync_to_async
    def mark_messages_read(self, sender_id):
        """Marcar como leídos los mensajes y notificaciones del emisor."""
        Message.objects.filter(
            recipient=self.user,
            sender_id=sender_id,
            is_read=False
        ).update(is_read=True)
        Notification.objects.filter(
            recipient=self.user,
            actor_id=sender_id,
            kind=Notification.KIND_MESSAGE,
            is_read=False
        ).update(is_read=True)

    @database_sync_to_async
    def get_unread_count(self):
        return Notification.unread_count(self.user)


class NotificationConsumer(AsyncWebsocketConsumer):
    """Canal global por usuario para notificaciones de mensajes nuevos.

    Cada usuario autenticado se une al grupo 'user_{id}' al conectar a
    /ws/notifications/. Se usa para refrescar el contador de los mensajes
    no leídos que se muestra en el header del sitio.
    """

    async def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            await self.close()
            return

        self.user_group_name = f"user_{self.user.id}"
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "user_group_name"):
            await self.channel_layer.group_discard(
                self.user_group_name,
                self.channel_name
            )

    async def notification_message(self, event):
        """Una notificación nueva llegó para este usuario."""
        await self.send(text_data=json.dumps({
            "type": "notif",
            "kind": event.get("kind", "message"),
            "sender_id": event["sender_id"],
            "sender_name": event["sender_name"],
            "preview": event["preview"],
            "room_url": event["room_url"],
        }))

    async def badge_update(self, event):
        """El servidor recalcula y envía el total exacto de no leídos."""
        await self.send(text_data=json.dumps({
            "type": "badge",
            "total": event["total"],
        }))