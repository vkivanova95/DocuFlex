from django.contrib import admin

from annexes.models import GeneratedAnnex


@admin.register(GeneratedAnnex)
class GeneratedAnnexAdmin(admin.ModelAdmin):
    list_display = ('request', 'annex_number', 'annex_date', 'file_path', 'created_at')
    list_filter = ('request', 'annex_number')
