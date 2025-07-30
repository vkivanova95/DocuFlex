from django import forms
from contracts.models import Currency, LoanType
from clients.models import Town


class CurrencyForm(forms.ModelForm):
    class Meta:
        model = Currency
        fields = ["currency_code", "currency_name", "is_active"]


class CreditTypeForm(forms.ModelForm):
    class Meta:
        model = LoanType
        fields = ["loan_type", "is_active"]


class TownForm(forms.ModelForm):
    class Meta:
        model = Town
        fields = ["name", "is_active"]
