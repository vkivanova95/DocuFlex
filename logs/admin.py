from django.contrib import admin
from .models import SystemLog

@admin.register(SystemLog)
class SystemLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'action', 'model_name', 'object_id', 'description')
    list_filter = ('action', 'model_name', 'user')
    search_fields = ('description', 'user__username')
    ordering = ('-timestamp',)

