from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django import forms
from django.shortcuts import redirect
from loan_requests.models import Request


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
        return user.is_authenticated and (
            user.is_superuser
            or user.groups.filter(name__in=self.allowed_groups).exists()
        )

    def handle_no_permission(self):
        messages.error(self.request, "Нямате достъп до тази функционалност.")
        return redirect("home")


class AnnexFormBehaviorMixin:
    hidden_fields = ["request_number", "annex_number", "annex_date", "city"]

    def apply_annex_form_behavior(self):
        # скривам някои полета
        for field in self.hidden_fields:
            if field in self.fields:
                self.fields[field].widget = forms.HiddenInput()

        # BooleanFields да използват чекбокс
        for name, field in self.fields.items():
            if isinstance(field, forms.BooleanField):
                field.widget = forms.CheckboxInput()


class AnnexPermissionMixin:
    # проверява дали текущият потребител е изпълнител по заявката
    def dispatch(self, request, *args, **kwargs):
        # админите имат пълен достъп
        if request.user.is_superuser or request.user.is_staff:
            return super().dispatch(request, *args, **kwargs)

        request_number = request.POST.get("request_number") or request.GET.get(
            "request_number"
        )

        if request_number:
            try:
                req_obj = Request.objects.get(request_number=request_number)
                if req_obj.maker != request.user:
                    messages.error(
                        request,
                        "Нямате право да работите по тази заявка – не сте нейният изпълнител.",
                    )
                    return redirect("annexes:generate_annex")
            except Request.DoesNotExist:
                messages.error(request, "Заявка с този номер не съществува.")
                return redirect("annexes:generate_annex")

        return super().dispatch(request, *args, **kwargs)


class PaginationMixin:
    default_paginate_by = 5

    def get_paginate_by(self, queryset):
        per_page = self.request.GET.get("per_page")
        if per_page == "all":
            return queryset.count()
        try:
            return int(per_page)
        except (TypeError, ValueError):
            return self.default_paginate_by


class FilterQuerysetMixin:
    # Прилага apply_filters() към queryset, ако го има в класа
    def get_queryset(self):
        queryset = super().get_queryset()
        if hasattr(self, "apply_filters"):
            return self.apply_filters(queryset)
        return queryset


class ContextQueryMixin:
    # Добавя q и per_page към контекста, използвани при търсене и страниране
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["q"] = self.request.GET.get("q", "")
        context["per_page"] = self.request.GET.get("per_page", str(self.paginate_by))
        return context
