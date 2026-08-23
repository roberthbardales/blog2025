from datetime import datetime, timedelta

from django.db import models
from django.template.defaultfilters import slugify
from model_utils.models import TimeStampedModel


class Tema(TimeStampedModel):
    """Banco de preguntas por tema"""

    nombre = models.CharField('Nombre', max_length=100, unique=True)
    descripcion = models.TextField('Descripción', blank=True)
    slug = models.SlugField(editable=False, max_length=120, unique=True)

    class Meta:
        verbose_name = 'Tema'
        verbose_name_plural = 'Temas'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        if not self.slug:
            now = datetime.now()
            total_time = timedelta(
                hours=now.hour,
                minutes=now.minute,
                seconds=now.second
            )
            seconds = int(total_time.total_seconds())
            slug_unique = '%s %s' % (self.nombre, str(seconds))
            self.slug = slugify(slug_unique)

        super(Tema, self).save(*args, **kwargs)

    @property
    def total_preguntas(self):
        return self.preguntas.count()


class Pregunta(TimeStampedModel):
    """Pregunta de un banco de preguntas"""

    FACIL = 'facil'
    MEDIO = 'medio'
    DIFICIL = 'dificil'

    NIVEL_CHOICES = (
        (FACIL, 'Fácil'),
        (MEDIO, 'Medio'),
        (DIFICIL, 'Difícil'),
    )

    tema = models.ForeignKey(
        Tema,
        on_delete=models.CASCADE,
        related_name='preguntas',
        verbose_name='Tema'
    )
    texto = models.TextField('Pregunta')
    nivel = models.CharField(
        'Nivel',
        max_length=10,
        choices=NIVEL_CHOICES,
        default=MEDIO
    )
    explicacion = models.TextField('Explicación', blank=True)

    class Meta:
        verbose_name = 'Pregunta'
        verbose_name_plural = 'Preguntas'
        ordering = ['-created']

    def __str__(self):
        return str(self.id) + '-' + self.texto[:50]


class Opcion(TimeStampedModel):
    """Opción de respuesta de una pregunta"""

    pregunta = models.ForeignKey(
        Pregunta,
        on_delete=models.CASCADE,
        related_name='opciones',
        verbose_name='Pregunta'
    )
    texto = models.TextField('Opción')
    es_correcta = models.BooleanField('Es correcta', default=False)

    class Meta:
        verbose_name = 'Opción'
        verbose_name_plural = 'Opciones'
        ordering = ['id']

    def __str__(self):
        return self.texto[:50]
