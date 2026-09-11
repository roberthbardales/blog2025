from django.db import models


class OfertaEmpleo(models.Model):
    api_id = models.CharField('ID API', max_length=500, unique=True, db_index=True)
    title = models.CharField('Título', max_length=300)
    company = models.CharField('Empresa', max_length=200, blank=True)
    location = models.CharField('Ubicación', max_length=200, blank=True)
    salary_min = models.IntegerField('Salario mínimo', null=True, blank=True)
    salary_max = models.IntegerField('Salario máximo', null=True, blank=True)
    currency_type = models.CharField('Moneda', max_length=10, blank=True)
    posted_date = models.DateTimeField('Fecha de publicación', null=True, blank=True)
    source = models.CharField('Fuente', max_length=250, blank=True)
    logo_url = models.URLField('Logo URL', max_length=500, blank=True)
    skills = models.JSONField('Habilidades', default=list, blank=True)
    level_rank = models.IntegerField('Rango de nivel', default=5)
    level = models.CharField('Nivel', max_length=30, blank=True)
    url = models.URLField('URL original', max_length=500, unique=True)
    oculto = models.BooleanField('Oculto', default=False)
    created = models.DateTimeField('Fecha de registro', auto_now_add=True)

    class Meta:
        verbose_name = 'Oferta de empleo'
        verbose_name_plural = 'Ofertas de empleo'
        ordering = ['-created']

    def __str__(self):
        return f"{self.title} - {self.company}" if self.company else self.title


class FiltroEmpleo(models.Model):
    nombre = models.CharField('Nombre del filtro', max_length=120)
    activo = models.BooleanField('Activo', default=True)

    keywords = models.TextField(
        'Palabras clave',
        help_text='Separadas por coma. Ej: python, django, linux',
        blank=True,
    )
    country_id = models.IntegerField('País (ID)', blank=True, null=True, help_text='Ej: 1 = Perú')
    from_age = models.IntegerField('Antigüedad en días', blank=True, null=True, help_text='Ej: 1 = último día')
    type_order = models.IntegerField('Orden de tipo', blank=True, null=True)
    job_seniority = models.JSONField('Niveles (seniority)', default=list, blank=True, help_text='IDs: 1 Prácticas, 2 Junior, 3 Semi Senior, 4 Senior')
    work_modality_id = models.JSONField('Modalidad de trabajo', default=list, blank=True)
    job_category_id = models.JSONField('Categoría', default=list, blank=True)
    job_type_id = models.JSONField('Tipo de empleo', default=list, blank=True)
    salary_min = models.IntegerField('Salario mínimo', blank=True, null=True)
    salary_max = models.IntegerField('Salario máximo', blank=True, null=True)
    currency_type = models.CharField('Moneda', max_length=10, blank=True)
    p_english_req = models.BooleanField('¿Requiere inglés?', null=True, blank=True)

    max_pages = models.IntegerField('Máx. páginas por keyword', default=3)

    email_destino = models.EmailField('Email de destino', blank=True, help_text='Vacío = usa el email configurado en el .env')
    telegram_chat_id = models.CharField('Telegram chat ID', max_length=64, blank=True, help_text='Vacío = usa el chat ID del .env')

    created = models.DateTimeField('Fecha de creación', auto_now_add=True)
    updated = models.DateTimeField('Fecha de actualización', auto_now=True)

    class Meta:
        verbose_name = 'Filtro de empleo'
        verbose_name_plural = 'Filtros de empleo'
        ordering = ['-created']

    def __str__(self):
        return self.nombre
