from django.db import models
from django.conf import settings
from model_utils.models import TimeStampedModel

class Nota(TimeStampedModel):
    # Colores disponibles para las notas (estilo Sticky Notes)
    AMARILLO = 'yellow'
    AZUL = 'blue'
    VERDE = 'green'
    ROSA = 'pink'
    NARANJA = 'orange'
    MORADO = 'purple'

    COLOR_CHOICES = (
        (AMARILLO, 'Amarillo'),
        (AZUL, 'Azul'),
        (VERDE, 'Verde'),
        (ROSA, 'Rosa'),
        (NARANJA, 'Naranja'),
        (MORADO, 'Morado'),
    )

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notas',
        verbose_name='Usuario'
    )
    titulo = models.CharField(
        'Título',
        max_length=100
    )
    contenido = models.TextField(
        'Contenido'
    )
    color = models.CharField(
        'Color',
        max_length=10,
        choices=COLOR_CHOICES,
        default=AMARILLO
    )
    es_importante = models.BooleanField(
        'Importante',
        default=False,
        help_text='Marcar nota como importante'
    )

    class Meta:
        verbose_name = 'Nota'
        verbose_name_plural = 'Notas'
        ordering = ['-es_importante', '-modified']

    def __str__(self):
        return f"{self.titulo} - {self.usuario.full_name}"