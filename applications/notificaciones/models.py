from django.conf import settings
from django.db import models
from model_utils.models import TimeStampedModel


class Notification(TimeStampedModel):
    KIND_MESSAGE = 'message'
    KIND_FRIEND_REQUEST = 'friend_request'
    KIND_FRIEND_ACCEPTED = 'friend_accepted'

    KIND_CHOICES = [
        (KIND_MESSAGE, 'Mensaje'),
        (KIND_FRIEND_REQUEST, 'Solicitud de amistad'),
        (KIND_FRIEND_ACCEPTED, 'Solicitud aceptada'),
    ]

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notificaciones',
        verbose_name='Destinatario'
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='+',
        verbose_name='Quién la genera'
    )
    kind = models.CharField(
        'Tipo',
        max_length=30,
        choices=KIND_CHOICES
    )
    text = models.CharField(
        'Texto',
        max_length=255
    )
    url = models.CharField(
        'Enlace',
        max_length=255,
        blank=True
    )
    is_read = models.BooleanField('Leída', default=False)

    class Meta:
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-created']

    def __str__(self):
        return f'{self.recipient} - {self.text[:40]}'

    @classmethod
    def unread_count(cls, user):
        return cls.objects.filter(recipient=user, is_read=False).count()

    @classmethod
    def recent(cls, user, limit=8):
        return cls.objects.filter(recipient=user).select_related('actor')[:limit]