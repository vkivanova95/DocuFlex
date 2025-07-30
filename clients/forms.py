from django import forms
from django.core.exceptions import ValidationError
from .models import Client, Town
from .validators import validate_represented_together
from common.forms import BaseStyledForm


class ClientForm(BaseStyledForm):
    class Meta:
        model = Client
        fields = "__all__"

        error_messages = {
            "eik": {
                "invalid": "ЕИК трябва да съдържа само цифри.",
                "unique": "Клиент с този ЕИК вече съществува.",
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["town"].queryset = Town.objects.filter(is_active=True)

        # Ако редактираме съществуващ клиент (т.е. имаме instance)
        if self.instance and self.instance.pk:
            self.fields["eik"].disabled = True

        # Показваме полето само ако клиентът вече съществува (при редакция)
        if self.instance.pk:
            self.fields["is_active"] = forms.BooleanField(
                label="Активен клиент", required=False
            )

    def clean_eik(self):
        eik = self.cleaned_data.get("eik")
        if Client.objects.filter(eik=eik).exclude(pk=self.instance.pk).exists():
            raise ValidationError("Клиент с този ЕИК вече съществува.")
        return eik

    def clean(self):
        cleaned_data = super().clean()
        validate_represented_together(cleaned_data)
        return cleaned_data


class EIKLookupForm(forms.Form):
    eik = forms.CharField(
        label="ЕИК",
        max_length=20,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        error_messages={"required": "Моля, въведете ЕИК."},
    )
