from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from common.constants import GROUP_MANAGER
from common.mixins import (
    GroupRequiredMixin,
    PaginationMixin,
    FilterQuerysetMixin,
    ContextQueryMixin,
)
from contracts.models import Currency, LoanType
from clients.models import Town
from .forms import CurrencyForm, CreditTypeForm, TownForm
from django.views.generic import ListView


class NomenclatureView(LoginRequiredMixin, GroupRequiredMixin, View):
    allowed_groups = [GROUP_MANAGER]

    def get(self, request):
        context = {
            "currencies": Currency.objects.all(),
            "credit_types": LoanType.objects.all(),
            "towns": Town.objects.all(),
            "currency_form": CurrencyForm(),
            "credit_form": CreditTypeForm(),
            "town_form": TownForm(),
        }
        return render(request, "nomenclatures/nomenclature_list.html", context)

    def post(self, request):
        if "add_currency" in request.POST:
            form = CurrencyForm(request.POST)
            if form.is_valid():
                form.save()
        elif "add_credit_type" in request.POST:
            form = CreditTypeForm(request.POST)
            if form.is_valid():
                form.save()
        elif "add_town" in request.POST:
            form = TownForm(request.POST)
            if form.is_valid():
                form.save()
        return redirect("nomenclatures:nomenclature_list")


class NomenclatureDeactivationView(LoginRequiredMixin, GroupRequiredMixin, View):
    allowed_groups = [GROUP_MANAGER]

    def post(self, request, model_name, pk):
        model_map = {
            "currency": Currency,
            "credit": LoanType,
            "town": Town,
        }
        model = model_map.get(model_name)
        if model:
            obj = get_object_or_404(model, pk=pk)
            obj.is_active = not obj.is_active
            obj.save()
        return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))


class CurrencyListView(
    LoginRequiredMixin,
    GroupRequiredMixin,
    PaginationMixin,
    FilterQuerysetMixin,
    ContextQueryMixin,
    ListView,
):
    model = Currency
    template_name = "nomenclatures/currency_list.html"
    context_object_name = "currencies"
    allowed_groups = [GROUP_MANAGER]
    ordering = ["currency_code"]

    def apply_filters(self, queryset):
        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = queryset.filter(
                Q(currency_name__icontains=query) | Q(currency_code__icontains=query)
            )
        return queryset


class LoanTypeListView(
    LoginRequiredMixin,
    GroupRequiredMixin,
    PaginationMixin,
    FilterQuerysetMixin,
    ContextQueryMixin,
    ListView,
):
    model = LoanType
    template_name = "nomenclatures/loan_type_list.html"
    context_object_name = "loan_types"
    allowed_groups = [GROUP_MANAGER]
    ordering = ["loan_type"]

    def apply_filters(self, queryset):
        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = queryset.filter(loan_type__icontains=query)
        return queryset


class TownListView(
    LoginRequiredMixin,
    GroupRequiredMixin,
    PaginationMixin,
    FilterQuerysetMixin,
    ContextQueryMixin,
    ListView,
):
    allowed_groups = [GROUP_MANAGER]
    model = Town
    template_name = "nomenclatures/town_list.html"
    context_object_name = "towns"
    ordering = ["name"]

    def apply_filters(self, queryset):
        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = queryset.filter(name__icontains=query)
        return queryset
