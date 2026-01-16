from django.db import models
from django.utils import timezone

# apps de terceros
from model_utils.models import TimeStampedModel

class Home(TimeStampedModel):
    title = models.CharField('Nombre', max_length=30)
    description = models.TextField()
    about_title = models.CharField('Titulo Nosotros', max_length=50)
    about_text = models.TextField()
    contact_email = models.EmailField('Email de Contacto', blank=True,null=True)
    phone = models.CharField('Telefono de Contacto', max_length=20)

    class Meta:
        verbose_name='Pagina Principal'
        verbose_name_plural='Pagina Principal'

    def __str__(self):
        return self.title

class Suscribers(TimeStampedModel):
    email = models.EmailField()

    class Meta:
        verbose_name='Suscriptor'
        verbose_name_plural='Suscriptores'

    def __str__(self):
        return self.email

class Contact(TimeStampedModel):

    full_name = models.CharField('Nombres', max_length=60)
    email = models.EmailField()
    messagge = models.TextField()
    class Meta:
        verbose_name='Contacto'
        verbose_name_plural='Mensajes'

    def __str__(self):
        return self.full_name


# models.py

class IPLocation(models.Model):
    """Almacena la información de geolocalización por IP"""
    ip_address = models.GenericIPAddressField(unique=True, db_index=True)
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    region = models.CharField(max_length=100, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "IP Location"
        verbose_name_plural = "IP Locations"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.ip_address} - {self.city}, {self.country}"


class VisitorLog(models.Model):
    """Registra cada visita al sitio"""
    ip_location = models.ForeignKey(
        IPLocation,
        on_delete=models.CASCADE,
        related_name='visits'
    )
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    user_agent = models.TextField(blank=True)  # Opcional: para saber navegador/dispositivo
    path = models.CharField(max_length=500, blank=True)  # Opcional: página visitada

    class Meta:
        verbose_name = "Visitor Log"
        verbose_name_plural = "Visitor Logs"
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.ip_location.ip_address} - {self.timestamp}"
