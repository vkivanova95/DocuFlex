from django import forms
from django.core.exceptions import ValidationError
from .models import Contract, Currency, LoanType
from clients.models import Client
from .validators import validate_active_client
from common.forms import BaseStyledForm, styled_datefield



class ContractForm(BaseStyledForm):
    eik = forms.CharField(label="ЕИК", max_length=20, required=True)
    name = forms.CharField(label="Име на фирмата", required=False, disabled=True)

    class Meta:
        model = Contract
        exclude = ['client']  # Скриваме оригиналното FK поле

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            self.fields['name'] = forms.CharField(
                label='Име на фирмата',
                initial=self.instance.client.name,
                required=False,
                disabled=True,
                widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'client_name'})
            )
        else:
            self.fields['name'] = forms.CharField(
                label='Име на фирмата',
                required=False,
                disabled=True,
                widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'client_name'})
            )

        # по подразбиране EUR ако формата е за добавяне на нов запис
        if not self.instance.pk:
            try:
                default_currency = Currency.objects.get(currency_code='EUR')
                self.fields['currency'].initial = default_currency
            except Currency.DoesNotExist:
                pass

        # ако редактираме съществуващ договор
        if self.instance and self.instance.pk:
            client = self.instance.client
            self.fields['eik'].initial = client.eik

        # само активни видове кредити и валути
        self.fields['loan_type'].queryset = LoanType.objects.filter(is_active=True)
        self.fields['currency'].queryset = Currency.objects.filter(is_active=True)

        # добавяне на placeholder към дата
        self.fields['start_date'] = styled_datefield()
        self.fields['start_date'].widget.attrs['placeholder'] = 'ДД-ММ-ГГГГ'

        # ако клиентът се инициализира с client_id
        client_id = self.initial.get('client_id')
        if client_id and not self.instance.pk:
            try:
                client = Client.objects.get(id=client_id)
                self.fields['eik'].initial = client.eik
                self.fields['name'].initial = client.name
                self.fields['eik'].disabled = True
            except Client.DoesNotExist:
                pass

    def clean_contract_number(self):
        contract_number = self.cleaned_data.get('contract_number')
        if Contract.objects.filter(contract_number=contract_number).exclude(pk=self.instance.pk).exists():
            raise ValidationError("Договор с този номер вече съществува.")
        return contract_number

    def clean_eik(self):
        eik = self.cleaned_data['eik']
        validate_active_client(eik)
        return eik

    def clean(self):
        cleaned_data = super().clean()
        eik = cleaned_data.get('eik')
        if eik:
            try:
                client = Client.objects.get(eik=eik, is_active=True)
                cleaned_data['client'] = client
            except Client.DoesNotExist:
                raise forms.ValidationError("Клиент с такъв ЕИК не съществува или е неактивен.")
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.client = self.cleaned_data['client']
        if commit:
            instance.save()
        return instance


