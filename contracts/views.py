from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.views.generic.edit import CreateView
from django.views.generic import FormView, UpdateView, ListView
from django.contrib import messages
from django.http import JsonResponse
from django.views import View
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from .models import Contract, Client
from .forms import ContractForm
from clients.forms import EIKLookupForm
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


class ContractCreateView(CreateView):
    model = Contract
    form_class = ContractForm
    template_name = 'contracts/contract_form.html'
    success_url = reverse_lazy('contracts:create')

    def form_valid(self, form):
        messages.success(self.request, "Договорът беше успешно записан.")
        return super().form_valid(form)


class GetClientNameView(View):
    def get(self, request):
        eik = request.GET.get("eik")
        try:
            client = Client.objects.get(eik=eik, is_active=True)
            return JsonResponse({"name": client.name})
        except Client.DoesNotExist:
            return JsonResponse({'error': 'Клиентът не е намерен.'}, status=404)


class ContractEikLookupView(FormView):
    template_name = 'contracts/contract_eik_lookup.html'
    form_class = EIKLookupForm

    def form_valid(self, form):
        eik = form.cleaned_data['eik']
        return redirect('contracts:contract_select', eik=eik)


class ContractSelectView(ListView):
    template_name = 'contracts/contract_select.html'
    context_object_name = 'contracts'

    def get_queryset(self):
        return Contract.objects.filter(client__eik=self.kwargs['eik'], is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['client'] = get_object_or_404(Client, eik=self.kwargs['eik'])
        return context


class ContractUpdateView(SuccessMessageMixin, UpdateView):
    model = Contract
    form_class = ContractForm
    template_name = 'contracts/contract_form.html'
    success_url = reverse_lazy('home')
    success_message = "Данните бяха успешно редактирани."

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['contract_number'].disabled = True  # Залостваме номера
        form.fields['eik'].disabled = True
        return form

    def form_valid(self, form):
        # self.object = form.save()
        # return redirect('home')
        return super().form_valid(form)


class ContractListView(ListView):
    model = Contract
    template_name = 'contracts/contract_list.html'
    context_object_name = 'contracts'
    paginate_by = 10

    def get_queryset(self):
        queryset = Contract.objects.select_related('client')
        search = self.request.GET.get('search', '')
        status = self.request.GET.get('status', '')

        if search:
            queryset = queryset.filter(
                Q(contract_number__icontains=search) |
                Q(client__eik__icontains=search)
            )
        if status:
            queryset = queryset.filter(is_active=(status == 'active'))

        return queryset

    def get_paginate_by(self, queryset):
        per_page = self.request.GET.get('per_page')
        if per_page == 'all':
            return queryset.count()
        return per_page or self.paginate_by


class ContractDeactivateView(View):
    @method_decorator(csrf_exempt)
    def post(self, request, pk):
        try:
            contract = Contract.objects.get(pk=pk)

            if not contract.is_active:
                messages.warning(request, "Договорът вече е деактивиран.")
            else:
                contract.is_active = False
                contract.save()
                messages.success(request, "Договорът беше успешно деактивиран.")

        except Contract.DoesNotExist:
            messages.error(request, "Договорът не беше намерен.")

        return redirect("contracts:list")