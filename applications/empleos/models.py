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
