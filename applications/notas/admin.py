from django.contrib import admin
from .models import Nota

class NotaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'usuario', 'color', 'es_importante', 'created', 'modified')
    list_filter = ('color', 'es_importante', 'created')
    search_fields = ('titulo', 'contenido', 'usuario__full_name', 'usuario__email')
    readonly_fields = ('created', 'modified')
    date_hierarchy = 'created'

    fieldsets = (
        ('Información básica', {
            'fields': ('usuario', 'titulo', 'contenido')
        }),
        ('Configuración', {
            'fields': ('color', 'es_importante')
        }),
        ('Fechas', {
            'fields': ('created', 'modified'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(usuario=request.user)

admin.site.register(Nota, NotaAdmin)