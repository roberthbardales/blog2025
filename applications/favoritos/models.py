from django.db import models
from django.conf import settings

# apps de terceros
from model_utils.models import TimeStampedModel

#
from applications.entrada.models import Entry

#
from .managers import FavoritesManager

class FavoriteGroup(TimeStampedModel):
    """ Grupos de favoritos creados por el usuario """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='favorite_groups',
        on_delete=models.CASCADE
    )
    name = models.CharField('Nombre del grupo', max_length=100)
    description = models.TextField('Descripción', blank=True, null=True)

    class Meta:
        verbose_name = 'Grupo de Favoritos'
        verbose_name_plural = 'Grupos de Favoritos'
        unique_together = ('user', 'name')

    def __str__(self):
        return f"{self.name} ({self.user})"



class Favorites(TimeStampedModel):
    """ Modelo para favotios """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='user_favorites',
        on_delete=models.CASCADE,
    )
    entry = models.ForeignKey(
        Entry,
        related_name='entry_favorites',
        on_delete=models.CASCADE
    )

    group = models.ForeignKey(
        FavoriteGroup,
        related_name='favorites',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )


    objects = FavoritesManager()

    class Meta:
        unique_together = ('user', 'entry')
        verbose_name = 'Entrada Favorita'
        verbose_name_plural = 'Entradas Favoritas'

    def __str__(self):
        return self.entry.title

