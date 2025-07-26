from django import forms
from annexes.mixins import StartFieldsMixin
from common.forms import BaseStyledSimpleForm, styled_datefield
from django.forms import formset_factory
from common.mixins import AnnexFormBehaviorMixin


class BaseAnnexStartForm(forms.Form):
    request_number = forms.CharField(label="Номер на заявка", widget=forms.TextInput(attrs={'class': 'form-control'}))
    annex_number = forms.CharField(label="Анекс №", widget=forms.TextInput(attrs={'class': 'form-control'}))
    annex_date = styled_datefield(label="Анекс дата")
    city = forms.CharField(label="Град", widget=forms.TextInput(attrs={'class': 'form-control'}))


class AnnexStandardForm(AnnexFormBehaviorMixin, StartFieldsMixin, BaseStyledSimpleForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_annex_form_behavior()

    def clean(self):
        cleaned_data = super().clean()
        amount_increase = cleaned_data.get("amount_increase")
        new_amount_increase = cleaned_data.get("new_amount_increase")

        if amount_increase and not new_amount_increase:
            self.add_error("new_amount_increase",
                           "Ако е попълнено поле Сума на увеличението, трябва да се попълни и поле Нов размер.")

        if new_amount_increase and not amount_increase:
            self.add_error("amount_increase", "Ако е попълнено поле Нов размер, трябва да се попълни и поле Сума на увеличението.")

        return cleaned_data

    new_amount_reduction = forms.CharField(required=False, widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'напр. 100 000.00 лева'}))
    amount_increase = forms.CharField(required=False, widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'напр. 100 000.00 лева'}))
    new_amount_increase = forms.CharField(required=False, widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'напр. 100 000.00 лева'}))

    stop_disbursement = forms.BooleanField(label="Прекратяване на усвояването", required=False)

    new_disbursement_date = styled_datefield(label="Нова дата на усвояване", required=False)
    new_repayment_date = styled_datefield(label="Нова дата на погасяване", required=False)
    effective_from = styled_datefield(label="Считано от", required=False)

    repayment_plan = forms.BooleanField(required=False)
    new_ceiling = forms.BooleanField(required=False)

    new_interest = forms.CharField(required=False, widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'напр. 3-месечен Юрибор + 5%'}))
    fee_review = forms.CharField(required=False, widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'напр. 1 000 лева'}))
    fee_management = forms.CharField(required=False, widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'напр. 0,5%'}))
    fee_commitment = forms.CharField(required=False, widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'напр. 0,5%'}))
    no_fees = forms.BooleanField(required=False)

    other_V = forms.CharField(label="Друго V", required=False)


class AnnexDeletionForm(AnnexFormBehaviorMixin, StartFieldsMixin, BaseAnnexStartForm):
    repaid_amount = forms.CharField(label="Погасена сума", required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'напр. 100 000 лева'}))
    deed_number = forms.CharField(label="Нотариален акт №", required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'напр. 102/31.01.2024'}))
    collateral_description = forms.CharField(label="Описание на обезпечението", required=True,widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'описание на заличавания имот'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_annex_form_behavior()


class AdditionalConditionForm(forms.Form):
    text = forms.CharField(label="", required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}))

AdditionalConditionFormSet = formset_factory(AdditionalConditionForm, extra=1, can_order=False, can_delete=True)
