from django import forms
from common.forms import styled_datefield


class StartFieldsMixin(forms.Form):
    request_number = forms.CharField()
    annex_number = forms.CharField()
    annex_date = styled_datefield(label="Анекс дата")
    city = forms.CharField()
