from django import forms
from django.forms import BooleanField


class BaseStyledForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if not isinstance(field, BooleanField):
                existing_classes = field.widget.attrs.get('class', '')
                field.widget.attrs['class'] = f"{existing_classes} form-control".strip()


class BaseStyledSimpleForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


def styled_datefield(label=None, required=True):
    return forms.DateField(
        label=label,
        required=required,
        widget=forms.DateInput(attrs={
            'type': 'text',
            'placeholder': 'ДД-ММ-ГГГГ',
            'class': 'form-control',
        }),
        input_formats=['%d-%m-%Y', '%Y-%m-%d'],
    )

