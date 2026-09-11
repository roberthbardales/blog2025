from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import Notification


def crear_notificacion(actor, recipient, kind, text, url=''):
    """Crea una notificación y la envía en vivo por WebSocket al destinatario."""
    notificacion = Notification.objects.create(
        recipient=recipient,
        actor=actor,
        kind=kind,
        text=text,
        url=url,
    )
    channel_layer = get_channel_layer()
    if channel_layer is not None:
        async_to_sync(channel_layer.group_send)(
            f"user_{recipient.id}",
            {
                "type": "notification_message",
                "kind": kind,
                "sender_id": actor.id if actor else None,
                "sender_name": actor.full_name if actor else "",
                "preview": text,
                "room_url": url,
            },
        )
    return notificacion


def marcar_todas_leidas(user):
    """Marca todas las notificaciones del usuario como leídas y sincroniza el badge."""
    actualizadas = Notification.objects.filter(
        recipient=user, is_read=False
    ).update(is_read=True)
    sincronizar_badge(user)
    return actualizadas


def marcar_mensajes_leidas(user, sender):
    """Marca como leídos los mensajes y notificaciones de chat de un emisor."""
    from applications.chat.models import Message

    Message.objects.filter(
        recipient=user, sender=sender, is_read=False
    ).update(is_read=True)
    Notification.objects.filter(
        recipient=user,
        actor=sender,
        kind=Notification.KIND_MESSAGE,
        is_read=False,
    ).update(is_read=True)
    sincronizar_badge(user)


def sincronizar_badge(user):
    """Empuja por WebSocket el total exacto de no leídos a las pestañas abiertas."""
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return
    total = Notification.unread_count(user)
    async_to_sync(channel_layer.group_send)(
        f"user_{user.id}",
        {"type": "badge_update", "total": total},
    )