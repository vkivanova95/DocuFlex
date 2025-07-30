from django import forms
from .models import CustomUser
from django.contrib.auth.models import Group


class UserCreateForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Служебна парола")
    group = forms.ModelChoiceField(queryset=Group.objects.all(), label="Група")

    class Meta:
        model = CustomUser
        fields = ["username", "email", "first_name", "last_name", "password", "group"]
        labels = {
            "username": "Потребителско име",
            "email": "Имейл адрес",
            "first_name": "Собствено име",
            "last_name": "Фамилия",
        }
        help_texts = {
            "username": "",
        }


class UserUpdateForm(forms.ModelForm):
    group = forms.ModelChoiceField(queryset=Group.objects.all(), label="Група")
    is_active = forms.BooleanField(label="Активен", required=False)

    class Meta:
        model = CustomUser
        fields = ["email", "first_name", "last_name", "group", "is_active"]

    def __init__(self, *args, **kwargs):
        user_instance = kwargs.get("instance")
        super().__init__(*args, **kwargs)
        if user_instance:
            groups = user_instance.groups.all()
            if groups.exists():
                self.fields["group"].initial = groups.first()


class PasswordResetForm(forms.Form):
    new_password = forms.CharField(
        widget=forms.PasswordInput, label="Нова служебна парола"
    )
