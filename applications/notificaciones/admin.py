from django.contrib import admin

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'kind', 'is_read', 'created']
    list_filter = ['kind', 'is_read', 'created']
    search_fields = ['recipient__email', 'text']
    list_select_related = ['recipient', 'actor']