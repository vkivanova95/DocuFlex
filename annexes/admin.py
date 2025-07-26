from django.contrib import admin
from annexes.models import GeneratedAnnex


@admin.register(GeneratedAnnex)
class GeneratedAnnexAdmin(admin.ModelAdmin):
    list_display = ('annex_number', 'request', 'annex_date', 'created_at', 'is_sent', 'send_attempts')
    list_filter = ('annex_date',)
    search_fields = ('annex_number', 'request__request_number', 'request__client__name')
    ordering = ('-annex_date',)
    readonly_fields = ('created_at',)
