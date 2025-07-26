from common.mixins import GroupRequiredMixin, PaginationMixin
from django.contrib.auth.mixins import LoginRequiredMixin
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
from logs.mixins import LogActionMixin


class ContractCreateView(LoginRequiredMixin, GroupRequiredMixin, LogActionMixin, CreateView):
    model = Contract
    form_class = ContractForm
    template_name = 'contracts/contract_form.html'
    success_url = reverse_lazy('contracts:create')
    allowed_groups = ['бизнес']
    action_type = 'create'

    def form_valid(self, form):
        messages.success(self.request, "Договорът беше успешно записан.")
        return super().form_valid(form)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if 'client' in form.fields:
            form.fields['client'].disabled = True
        return form

    def get_initial(self):
        initial = super().get_initial()
        client_id = self.request.GET.get('client_id')
        if client_id:
            initial['client_id'] = client_id
        return initial


class GetClientNameView(LoginRequiredMixin, GroupRequiredMixin, View):
    allowed_groups = ['бизнес']
    def get(self, request):
        eik = request.GET.get("eik")
        try:
            client = Client.objects.get(eik=eik, is_active=True)
            return JsonResponse({"name": client.name})
        except Client.DoesNotExist:
            return JsonResponse({'error': 'Клиентът не е намерен.'}, status=404)


class ContractEikLookupView(LoginRequiredMixin, GroupRequiredMixin, FormView):
    template_name = 'contracts/contract_eik_lookup.html'
    form_class = EIKLookupForm
    allowed_groups = ['бизнес']

    def form_valid(self, form):
        eik = form.cleaned_data['eik']
        return redirect('contracts:contract_select', eik=eik)


class ContractSelectView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    template_name = 'contracts/contract_select.html'
    context_object_name = 'contracts'
    allowed_groups = ['бизнес']

    def get_queryset(self):
        return Contract.objects.filter(client__eik=self.kwargs['eik'], is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['client'] = get_object_or_404(Client, eik=self.kwargs['eik'])
        return context


class ContractUpdateView(LoginRequiredMixin, GroupRequiredMixin, SuccessMessageMixin, LogActionMixin, UpdateView):
    model = Contract
    form_class = ContractForm
    template_name = 'contracts/contract_form.html'
    success_url = reverse_lazy('home')
    success_message = "Данните бяха успешно редактирани."
    allowed_groups = ['бизнес']
    action_type = 'edit'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['contract_number'].disabled = True
        form.fields['eik'].disabled = True
        return form

    def form_valid(self, form):
        return super().form_valid(form)


class ContractListView(LoginRequiredMixin, GroupRequiredMixin, PaginationMixin, ListView):
    model = Contract
    template_name = 'contracts/contract_list.html'
    context_object_name = 'contracts'
    allowed_groups = ['бизнес', 'ръководител', 'изпълнител']

    def get_queryset(self):
        queryset = Contract.objects.select_related('client')
        return self.apply_filters(queryset)

    def apply_filters(self, queryset):
        search = self.request.GET.get('search', '')
        status = self.request.GET.get('status', '')

        if search:
            queryset = queryset.filter(
                Q(contract_number__icontains=search) |
                Q(client__eik__icontains=search)
            )

        if status in ['active', 'inactive']:
            queryset = queryset.filter(is_active=(status == 'active'))

        return queryset


class ContractDeactivateView(LoginRequiredMixin, GroupRequiredMixin, View):
    allowed_groups = ['бизнес']

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