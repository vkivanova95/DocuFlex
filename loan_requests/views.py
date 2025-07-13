from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from common.forms import BaseStyledForm
from .forms import RequestForm, RequestExecutionForm
from django.views.generic import View, UpdateView, DetailView, ListView
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from clients.models import Client
from clients.forms import EIKLookupForm
from contracts.models import Contract
from django.shortcuts import render, get_object_or_404, redirect
from .models import Request
from .utils import get_executors
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required


class RequestCreateForm(BaseStyledForm):
    class Meta:
        model = Request
        fields = ['client', 'loan_agreement', 'document_type']
        widgets = {
            'document_type': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['loan_agreement'].queryset = Contract.objects.filter(is_active=True)

class RequestEIKSearchView(View):
    def get(self, request):
        form = EIKLookupForm()
        return render(request, 'requests/eik_search.html', {'form': form})

    def post(self, request):
        form = EIKLookupForm(request.POST)
        if form.is_valid():
            eik = form.cleaned_data['eik']
            try:
                client = Client.objects.get(eik=eik)  # без is_active=True

                if not client.is_active:
                    return render(request, 'requests/eik_search.html', {
                        'form': form,
                        'inactive_client': True,
                        'client_id': client.id,
                        'eik': eik,
                    })

                # Клиентът е активен
                contracts = Contract.objects.filter(client=client, is_active=True)
                if not contracts.exists():
                    return render(request, 'requests/eik_search.html', {
                        'form': form,
                        'error': 'Няма активни договори за този клиент.',
                        'show_create_contract': True,
                        'client_id': client.id,
                    })

                return render(request, 'requests/select_contract.html', {
                    'client': client,
                    'contracts': contracts
                })

            except Client.DoesNotExist:
                return render(request, 'requests/eik_search.html', {
                    'form': form,
                    'client_not_found': True,
                    'eik': eik
                })

        return render(request, 'requests/eik_search.html', {'form': form})


class RequestFinalizeView(View):

    def post(self, request):
        client_id = request.POST.get('client_id')
        loan_agreement_id = request.POST.get('loan_agreement_id')

        client = get_object_or_404(Client, id=client_id, is_active=True)
        loan_agreement = get_object_or_404(Contract, id=loan_agreement_id, is_active=True)

        # Попълване на формата с предварително зададени стойности
        initial_data = {
            'client': client,
            'loan_agreement': loan_agreement,
        }
        form = RequestCreateForm(initial=initial_data)

        return render(request, 'requests/request_finalize.html', {
            'form': form,
            'client': client,
            'loan_agreement': loan_agreement,
            'amount': loan_agreement.amount,
            'currency': loan_agreement.currency,
        })

    def get(self, request):
        return HttpResponseRedirect(reverse('requests:request_add'))  # защита от ръчно писане на GET


class RequestSubmitView(View):
    def post(self, request):
        form = RequestForm(request.POST)
        if form.is_valid():
            new_request = form.save(commit=False)
            new_request.amount = request.POST.get('amount')
            new_request.currency = new_request.loan_agreement.currency
            new_request.save()
            messages.success(request, f"Заявката е създадена успешно. Номер на заявка: {new_request.request_number}")

            # Успешно създаване – генерирай номер
            return redirect('requests:request_add')

        # Ако невалидно – формата
        return render(request, 'requests/request_finalize.html', {'form': form})

class AssignRequestsView(View):
    def get(self, request):
        pending_requests = Request.objects.filter(maker__isnull=True)
        executors = get_executors()
        return render(request, 'requests/assign_requests.html', {
            'pending_requests': pending_requests,
            'executors': executors,
        })

    def post(self, request):
        executor_id = request.POST.get('maker')
        selected_ids = request.POST.getlist('selected_requests')

        if executor_id and selected_ids:
            Request.objects.filter(id__in=selected_ids).update(maker_id=executor_id)
            messages.success(request, 'Заявките бяха разпределени успешно.')

        return redirect('requests:assign_requests')


@method_decorator(login_required, name='dispatch')
class AssignedRequestsListView(View):
    def get(self, request):
        current_user = request.user
        selected_executor_id = request.GET.get('executor')

        executors = get_executors()
        requests_qs = Request.objects.filter(maker__isnull=False)

        if selected_executor_id:
            if selected_executor_id != 'all':
                requests_qs = requests_qs.filter(maker_id=selected_executor_id)
        else:
            # Ако не е избрано нищо – по подразбиране се показват заявките на текущия потребител
            requests_qs = requests_qs.filter(maker=current_user)

        return render(request, 'requests/assigned_requests.html', {
            'requests': requests_qs,
            'executors': executors,
            'selected_executor': selected_executor_id or str(current_user.id),
        })

class RequestDetailView(LoginRequiredMixin, UpdateView):
    model = Request
    form_class = RequestExecutionForm
    template_name = 'requests/request_detail.html'
    success_url = reverse_lazy('requests:assigned_requests')

    def form_valid(self, form):
        messages.success(self.request, 'Заявката беше успешно актуализирана.')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class RequestListView(ListView):
    model = Request
    template_name = 'requests/request_list_all.html'
    context_object_name = 'requests'
    paginate_by = 10

    def get_queryset(self):
        queryset = Request.objects.select_related('client', 'loan_agreement', 'maker').all()

        name = self.request.GET.get('name', '')
        eik = self.request.GET.get('eik', '')
        contract = self.request.GET.get('contract', '')
        maker = self.request.GET.get('maker', '')
        document_type = self.request.GET.get('document_type', '')
        status = self.request.GET.get('status', '')

        if name:
            queryset = queryset.filter(client__name__icontains=name)
        if eik:
            queryset = queryset.filter(client__eik__icontains=eik)
        if contract:
            queryset = queryset.filter(loan_agreement__contract_number__icontains=contract)
        if maker:
            queryset = queryset.filter(maker_id=maker)
        if document_type:
            queryset = queryset.filter(document_type=document_type)
        if status:
            queryset = queryset.filter(status=status)

        return queryset

    def get_paginate_by(self, queryset):
        per_page = self.request.GET.get('per_page')
        if per_page == 'all':
            return queryset.count()
        return per_page or self.paginate_by

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['makers'] = get_executors()
        context['filters'] = {
            'name': self.request.GET.get('name', ''),
            'eik': self.request.GET.get('eik', ''),
            'contract': self.request.GET.get('contract', ''),
            'maker': self.request.GET.get('maker', ''),
            'document_type': self.request.GET.get('document_type', ''),
            'status': self.request.GET.get('status', ''),
        }
        context['per_page'] = self.get_paginate_by(self.get_queryset())
        return context

@method_decorator(login_required, name='dispatch')
class RequestDetailReadOnlyView(DetailView):
    model = Request
    template_name = 'requests/request_detail_readonly.html'
    context_object_name = 'request_obj'
