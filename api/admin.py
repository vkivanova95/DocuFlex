from django.contrib import admin
from api.models import SignatureLog


@admin.register(SignatureLog)
class SignatureLogAdmin(admin.ModelAdmin):
    list_display = (
        "annex_number",
        "request",
        "user",
        "sent_at",
        "status",
        "is_signed_successfully",
    )
    list_filter = ("status", "is_signed_successfully", "sent_at")
    search_fields = (
        "annex_number",
        "request__request_number",
        "user__username",
        "response_message",
    )
    readonly_fields = (
        "sent_at",
        "user",
        "annex_number",
        "file_sent",
        "status",
        "response_message",
        "is_signed_successfully",
        "request",
    )
    ordering = ("-sent_at",)
