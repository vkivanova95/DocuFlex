from django.contrib import admin
from .models import LoanType, Currency, Contract

@admin.register(LoanType)
class LoanTypeAdmin(admin.ModelAdmin):
    list_display = ('loan_type', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('loan_type',)

@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('currency_code', 'currency_name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('currency_code', 'currency_name')

@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ('contract_number', 'client', 'start_date', 'loan_type', 'currency', 'amount', 'is_active')
    list_filter = ('is_active', 'currency', 'loan_type')
    search_fields = ('contract_number', 'client__name', 'client__eik')
