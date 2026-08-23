from django.contrib import admin

from .models import Opcion, Pregunta, Tema


class OpcionInline(admin.TabularInline):
    model = Opcion
    extra = 4


@admin.register(Pregunta)
class PreguntaAdmin(admin.ModelAdmin):
    inlines = [OpcionInline]
    list_display = ('texto', 'tema', 'nivel', 'created')
    list_filter = ('tema', 'nivel', 'created')
    search_fields = ('texto',)
    readonly_fields = ('created', 'modified')


@admin.register(Tema)
class TemaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'total_preguntas', 'created')
    search_fields = ('nombre',)
    prepopulated_fields = {}
    readonly_fields = ('slug', 'created', 'modified')
