from django.contrib import admin
from .models import FiltroEmpleo, OfertaEmpleo


@admin.register(OfertaEmpleo)
class OfertaEmpleoAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'level', 'source', 'location', 'created')
    list_filter = ('level', 'source', 'created')
    search_fields = ('title', 'company', 'location')
    readonly_fields = ('created',)
    date_hierarchy = 'created'


@admin.register(FiltroEmpleo)
class FiltroEmpleoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activo', 'keywords', 'country_id', 'created')
    list_filter = ('activo', 'created')
    search_fields = ('nombre', 'keywords')
    readonly_fields = ('created', 'updated')
    fieldsets = (
        ('General', {
            'fields': ('nombre', 'activo', 'keywords', 'max_pages'),
        }),
        ('Filtros de búsqueda', {
            'fields': (
                'country_id', 'from_age', 'type_order',
                'job_seniority', 'work_modality_id',
                'job_category_id', 'job_type_id',
                'salary_min', 'salary_max',
                'currency_type', 'p_english_req',
            ),
        }),
        ('Destinos de notificación', {
            'fields': ('email_destino', 'telegram_chat_id'),
        }),
        ('Metadatos', {
            'fields': ('created', 'updated'),
        }),
    )
