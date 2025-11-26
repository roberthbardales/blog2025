from django.contrib import admin
from .models import Message

class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'recipient', 'content', 'created', 'is_read']  # created en vez de created_at
    list_filter = ['created', 'is_read']  # created en vez de created_at
    search_fields = ['sender__email', 'recipient__email', 'content']

admin.site.register(Message, MessageAdmin)
