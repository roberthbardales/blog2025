from django.contrib import admin
from .models import OfertaEmpleo, Busqueda


@admin.register(OfertaEmpleo)
class OfertaEmpleoAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'level', 'source', 'location', 'created')
    list_filter = ('level', 'source', 'created')
    search_fields = ('title', 'company', 'location')
    readonly_fields = ('created',)
    date_hierarchy = 'created'


@admin.register(Busqueda)
class BusquedaAdmin(admin.ModelAdmin):
    list_display = ('keyword', 'total_encontradas', 'nuevas', 'existentes', 'created')
    search_fields = ('keyword',)
    readonly_fields = ('created',)
    date_hierarchy = 'created'
