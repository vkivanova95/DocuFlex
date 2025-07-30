from django.contrib import admin
from .models import Request


@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = (
        "request_number",
        "client",
        "loan_agreement",
        "amount",
        "currency",
        "status",
        "maker",
        "created_at",
    )
    list_filter = ("status", "currency", "document_type", "maker")
    search_fields = (
        "request_number",
        "client__name",
        "client__eik",
        "loan_agreement__contract_number",
    )
    ordering = ("-created_at",)
    readonly_fields = ("request_number", "created_at")
