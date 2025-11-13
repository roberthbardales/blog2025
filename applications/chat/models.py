from django.db import models
from django.utils import timezone

#local
from applications.users.models import User

#app terceros
from model_utils.models import TimeStampedModel

class Message(TimeStampedModel):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['created']  # Cambiar de 'created_at' a 'created'

    def __str__(self):
        return f'{self.sender} -> {self.recipient}: {self.content[:20]}'



class UserStatus(models.Model):
    """
    Opcional: si quieres mostrar usuarios online/offline.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.get_full_name()} - {'Online' if self.is_online else 'Offline'}"


