from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django import forms


class SuccessMessageMixin:
    success_message = None

    def form_valid(self, form):
        if self.success_message:
            messages.success(self.request, self.success_message)
        return super().form_valid(form)


class GroupRequiredMixin(UserPassesTestMixin):
    allowed_groups = []
    def test_func(self):
        user = self.request.user
        return (
            user.is_authenticated and (
                user.is_superuser or
                user.groups.filter(name__in=self.allowed_groups).exists()
            )
        )


class AnnexFormBehaviorMixin:
    hidden_fields = ['request_number', 'annex_number', 'annex_date', 'city']

    def apply_annex_form_behavior(self):
        # скривам някои полета
        for field in self.hidden_fields:
            if field in self.fields:
                self.fields[field].widget = forms.HiddenInput()

        # BooleanFields да използват чекбокс
        for name, field in self.fields.items():
            if isinstance(field, forms.BooleanField):
                field.widget = forms.CheckboxInput()
