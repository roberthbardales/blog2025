from django.contrib import admin
from .models import OfertaEmpleo


@admin.register(OfertaEmpleo)
class OfertaEmpleoAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'level', 'source', 'location', 'created')
    list_filter = ('level', 'source', 'created')
    search_fields = ('title', 'company', 'location')
    readonly_fields = ('created',)
    date_hierarchy = 'created'
