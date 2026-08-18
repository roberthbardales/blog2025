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


class Servicio(TimeStampedModel):
    """Servicio web/sistema que se ofrece con precio y descripción."""

    COLOR_CLASSES = {
        'emerald': {
            'borde': 'border-emerald-500',
            'icono_bg': 'bg-emerald-500/10',
            'icono_txt': 'text-emerald-400',
            'btn': 'bg-emerald-600 hover:bg-emerald-700 shadow-emerald-500/20',
        },
        'blue': {
            'borde': 'border-blue-500',
            'icono_bg': 'bg-blue-500/10',
            'icono_txt': 'text-blue-400',
            'btn': 'bg-blue-600 hover:bg-blue-700 shadow-blue-500/20',
        },
        'amber': {
            'borde': 'border-amber-500',
            'icono_bg': 'bg-amber-500/10',
            'icono_txt': 'text-amber-400',
            'btn': 'bg-amber-600 hover:bg-amber-700 shadow-amber-500/20',
        },
        'purple': {
            'borde': 'border-purple-500',
            'icono_bg': 'bg-purple-500/10',
            'icono_txt': 'text-purple-400',
            'btn': 'bg-purple-600 hover:bg-purple-700 shadow-purple-500/20',
        },
        'pink': {
            'borde': 'border-pink-500',
            'icono_bg': 'bg-pink-500/10',
            'icono_txt': 'text-pink-400',
            'btn': 'bg-pink-600 hover:bg-pink-700 shadow-pink-500/20',
        },
        'teal': {
            'borde': 'border-teal-500',
            'icono_bg': 'bg-teal-500/10',
            'icono_txt': 'text-teal-400',
            'btn': 'bg-teal-600 hover:bg-teal-700 shadow-teal-500/20',
        },
        'yellow': {
            'borde': 'border-yellow-500',
            'icono_bg': 'bg-yellow-500/10',
            'icono_txt': 'text-yellow-400',
            'btn': 'bg-yellow-600 hover:bg-yellow-700 shadow-yellow-500/20',
        },
        'indigo': {
            'borde': 'border-indigo-500',
            'icono_bg': 'bg-indigo-500/10',
            'icono_txt': 'text-indigo-400',
            'btn': 'bg-indigo-600 hover:bg-indigo-700 shadow-indigo-500/20',
        },
        'slate': {
            'borde': 'border-slate-400',
            'icono_bg': 'bg-slate-400/10',
            'icono_txt': 'text-slate-400',
            'btn': 'bg-slate-600 hover:bg-slate-700 shadow-slate-500/20',
        },
        'primary': {
            'borde': 'border-primary-500',
            'icono_bg': 'bg-primary-500/10',
            'icono_txt': 'text-primary-500',
            'btn': 'bg-primary-600 hover:bg-primary-700 shadow-primary-500/20',
        },
    }

    nombre = models.CharField('Nombre', max_length=100)
    descripcion = models.TextField('Descripción')
    precio = models.DecimalField('Precio (S/)', max_digits=10, decimal_places=2, null=True, blank=True)
    caracteristicas = models.JSONField(
        'Características',
        default=list,
        blank=True,
        help_text='Lista de características. Una por elemento, ej. ["Punto de venta", "Facturación"].',
    )
    icono = models.CharField(
        'Ícono (FontAwesome)',
        max_length=80,
        default='fas fa-cogs',
        help_text='Clase de FontAwesome, ej. "fas fa-cash-register".',
    )
    color = models.CharField(
        'Color (Tailwind)',
        max_length=30,
        default='primary',
        help_text='Nombre del color de acento: blue, amber, purple, pink, teal, yellow, indigo, slate o primary.',
    )
    destacado = models.BooleanField('Destacado / Recomendado', default=False)
    activo = models.BooleanField('Activo', default=True)
    orden = models.PositiveIntegerField('Orden', default=0)

    class Meta:
        verbose_name = 'Servicio'
        verbose_name_plural = 'Servicios'
        ordering = ['orden', 'id']

    def __str__(self):
        if not self.precio:
            return f"{self.nombre} - Sin precio"
        return f"{self.nombre} - S/ {self.precio}"

    @property
    def clases(self):
        """Clases Tailwind según el color definido en el admin."""
        return self.COLOR_CLASSES.get(self.color, self.COLOR_CLASSES['primary'])
