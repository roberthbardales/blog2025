from django.contrib import admin
#
from .models import Home,Suscribers,Contact

admin.site.register(Home)
admin.site.register(Suscribers)
admin.site.register(Contact)

# admin.py
from .models import IPLocation, VisitorLog

@admin.register(IPLocation)
class IPLocationAdmin(admin.ModelAdmin):
    list_display = ['ip_address', 'city', 'country', 'created_at']
    search_fields = ['ip_address', 'city', 'country']
    list_filter = ['country', 'created_at']

@admin.register(VisitorLog)
class VisitorLogAdmin(admin.ModelAdmin):
    list_display = ['ip_location', 'timestamp', 'path']
    list_filter = ['timestamp']
    date_hierarchy = 'timestamp'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('ip_location')