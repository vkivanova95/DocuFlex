from django import forms
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from .models import Request
from contracts.models import Contract
from common.forms import BaseStyledForm
from common.forms import styled_datefield


class RequestForm(BaseStyledForm):
    class Meta:
        model = Request
        fields = ['client', 'loan_agreement', 'document_type']
        widgets = {
            'document_type': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['loan_agreement'].queryset = Contract.objects.filter(is_active=True)


class RequestExecutionForm(BaseStyledForm):
    YES_NO_CHOICES = (
        ('', '---'),
        ('true', 'Да'),
        ('false', 'Не'),
    )

    correction_required = forms.ChoiceField(choices=YES_NO_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}),
                                            label='Корекции по документа', required=False)
    preparation_date = styled_datefield(label='Дата на изготвяне', required=False)
    signing_date = styled_datefield(label='Дата на подписване', required=False)

    class Meta:
        model = Request
        fields = ['preparation_date', 'correction_required', 'signing_date', 'status']

    def clean_correction_required(self):
        value = self.cleaned_data['correction_required']
        if value == '':
            return None
        return value == 'true'

    def post(self, request, pk):
        req = get_object_or_404(Request, pk=pk)
        form = RequestExecutionForm(request.POST, instance=req)

        if form.is_valid():
            form.save()
            messages.success(request, "Заявката е обновена успешно.")
            return_to = request.GET.get('return_to', reverse_lazy('requests:assigned_requests'))
            return redirect(return_to)

        return render(request, 'requests/request_detail.html', {
            'form': form,
            'request_obj': req,
        })
