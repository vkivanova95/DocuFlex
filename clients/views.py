from common.mixins import GroupRequiredMixin, PaginationMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.shortcuts import render
from django.views import View
from django.views.generic import CreateView, UpdateView, ListView
from django.urls import reverse_lazy, reverse
from .models import Client
from .forms import ClientForm, EIKLookupForm
from django.contrib import messages
from django.shortcuts import redirect
from logs.mixins import LogActionMixin


class ClientCreateView(LoginRequiredMixin, GroupRequiredMixin, SuccessMessageMixin, LogActionMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = 'clients/client_form.html'
    success_url = reverse_lazy('home')
    success_message = "Клиентът беше успешно създаден."
    allowed_groups = ['бизнес']
    action_type = 'create'

    def form_valid(self, form):
        form.instance.is_active = True
        return super().form_valid(form)

    def get_initial(self):
        initial = super().get_initial()
        eik = self.request.GET.get('eik')
        if eik:
            initial['eik'] = eik
        return initial


class ClientUpdateView(LoginRequiredMixin, GroupRequiredMixin, SuccessMessageMixin, LogActionMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = 'clients/client_form.html'
    success_url = reverse_lazy('home')
    success_message = "Данните бяха успешно редактирани."
    allowed_groups = ['бизнес']
    action_type = 'edit'

    def form_valid(self, form):
        return super().form_valid(form)

    def get_success_url(self):
        return_url = self.request.GET.get('return_to')
        if return_url:
            return reverse(return_url)
        return reverse('home')


class ClientEIKLookupView(LoginRequiredMixin, GroupRequiredMixin, View):
    template_name = 'clients/client_eik_lookup.html'
    allowed_groups = ['бизнес']

    def get(self, request):
        form = EIKLookupForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = EIKLookupForm(request.POST)
        if form.is_valid():
            eik = form.cleaned_data['eik']
            try:
                client = Client.objects.get(eik=eik)
                return redirect('clients:edit', pk=client.pk)
            except Client.DoesNotExist:
                messages.error(request, f"Клиент с ЕИК {eik} не съществува.")
        return render(request, self.template_name, {'form': form})


class ClientListView(LoginRequiredMixin, GroupRequiredMixin, PaginationMixin, ListView):
    model = Client
    template_name = 'clients/client_list.html'
    context_object_name = 'clients'
    allowed_groups = ['бизнес', 'ръководител', 'изпълнител']

    def get_queryset(self):
        queryset = Client.objects.all().order_by('name')
        search_query = self.request.GET.get('search', '').strip()

        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) | Q(eik__icontains=search_query)
            )

        status_filter = self.request.GET.get('status')
        if status_filter == 'active':
            queryset = queryset.filter(is_active=True)
        elif status_filter == 'inactive':
            queryset = queryset.filter(is_active=False)

        return queryset.order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        return context


class ClientDeactivateView(LoginRequiredMixin, GroupRequiredMixin, View):
    allowed_groups = ['бизнес']

    def post(self, request, pk):
        try:
            client = Client.objects.get(pk=pk)

            if not client.is_active:
                messages.warning(request, "Клиентът вече е деактивиран.")
            else:
                client.is_active = False
                client.save()
                messages.success(request, "Клиентът беше успешно деактивиран.")

        except Client.DoesNotExist:
            messages.error(request, "Клиентът не беше намерен.")

        return redirect("clients:list")
