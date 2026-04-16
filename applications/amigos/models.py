from django.db import models
from django.conf import settings
from model_utils.models import TimeStampedModel
from .managers import FriendshipManager

class Friendship(TimeStampedModel):

    STATUS_PENDING  = 'pending'
    STATUS_ACCEPTED = 'accepted'
    STATUS_REJECTED = 'rejected'
    STATUS_BLOCKED  = 'blocked'

    STATUS_CHOICES = [
        (STATUS_PENDING,  'Pendiente'),
        (STATUS_ACCEPTED, 'Aceptado'),
        (STATUS_REJECTED, 'Rechazado'),
        (STATUS_BLOCKED,  'Bloqueado'),
    ]

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='sent_requests',
        on_delete=models.CASCADE,
        verbose_name='Solicitante'
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='received_requests',
        on_delete=models.CASCADE,
        verbose_name='Receptor'
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING
    )

    # dentro de Friendship:
    objects = FriendshipManager()

    class Meta:
        unique_together = ('sender', 'receiver')
        verbose_name = 'Amistad'
        verbose_name_plural = 'Amistades'

    def __str__(self):
        return f"{self.sender} -> {self.receiver} [{self.status}]"