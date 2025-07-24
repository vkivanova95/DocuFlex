from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from common.mixins import GroupRequiredMixin
from contracts.models import Currency, LoanType
from clients.models import Town
from .forms import CurrencyForm, CreditTypeForm, TownForm
from django.views.generic import ListView


class NomenclatureView(LoginRequiredMixin, GroupRequiredMixin, View):
    allowed_groups = ['ръководител']

    def get(self, request):
        context = {
            'currencies': Currency.objects.all(),
            'credit_types': LoanType.objects.all(),
            'towns': Town.objects.all(),
            'currency_form': CurrencyForm(),
            'credit_form': CreditTypeForm(),
            'town_form': TownForm(),
        }
        return render(request, 'nomenclatures/nomenclature_list.html', context)

    def post(self, request):
        if 'add_currency' in request.POST:
            form = CurrencyForm(request.POST)
            if form.is_valid():
                form.save()
        elif 'add_credit_type' in request.POST:
            form = CreditTypeForm(request.POST)
            if form.is_valid():
                form.save()
        elif 'add_town' in request.POST:
            form = TownForm(request.POST)
            if form.is_valid():
                form.save()
        return redirect('nomenclatures:nomenclature_list')


class NomenclatureDeactivationView(LoginRequiredMixin, GroupRequiredMixin, View):
    allowed_groups = ['ръководител']

    def post(self, request, model_name, pk):
        model_map = {
            'currency': Currency,
            'credit': LoanType,
            'town': Town,
        }
        model = model_map.get(model_name)
        if model:
            obj = get_object_or_404(model, pk=pk)
            obj.is_active = not obj.is_active
            obj.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


class CurrencyListView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    allowed_groups = ['ръководител']
    model = Currency
    template_name = 'nomenclatures/currency_list.html'
    context_object_name = 'currencies'

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        qs = super().get_queryset().order_by('currency_name')
        if query:
            qs = qs.filter(currency_name__icontains=query) | qs.filter(currency_code__icontains=query)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context


class LoanTypeListView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    allowed_groups = ['ръководител']
    model = LoanType
    template_name = 'nomenclatures/loan_type_list.html'
    context_object_name = 'loan_types'

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        qs = super().get_queryset().order_by('loan_type')
        if query:
            qs = qs.filter(loan_type__icontains=query)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context


class TownListView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    allowed_groups = ['ръководител']
    model = Town
    template_name = 'nomenclatures/town_list.html'
    context_object_name = 'towns'

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        qs = super().get_queryset().order_by('name')
        if query:
            qs = qs.filter(name__icontains=query)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context