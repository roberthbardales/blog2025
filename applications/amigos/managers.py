from django.db import models
from django.db.models import Q


class FriendshipManager(models.Manager):

    def get_friends(self, user):
        """Retorna los usuarios amigos confirmados"""
        return self.filter(
            Q(sender=user) | Q(receiver=user),
            status='accepted'
        )

    def get_pending_received(self, user):
        """Solicitudes que el usuario ha recibido y aún no responde"""
        return self.filter(receiver=user, status='pending')

    def get_pending_sent(self, user):
        """Solicitudes enviadas por el usuario"""
        return self.filter(sender=user, status='pending')

    def are_friends(self, user1, user2):
        return self.filter(
            Q(sender=user1, receiver=user2) |
            Q(sender=user2, receiver=user1),
            status='accepted'
        ).exists()

    def get_friendship(self, user1, user2):
        return self.filter(
            Q(sender=user1, receiver=user2) |
            Q(sender=user2, receiver=user1)
        ).first()