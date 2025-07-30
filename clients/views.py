from common.constants import GROUP_BUSINESS, GROUP_MANAGER, GROUP_MAKER
from common.mixins import (
    GroupRequiredMixin,
    PaginationMixin,
    FilterQuerysetMixin,
    ContextQueryMixin,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.shortcuts import render
from django.views import View
from django.views.generic import CreateView, UpdateView, ListView
from django.urls import reverse_lazy
from .models import Client
from .forms import ClientForm, EIKLookupForm
from django.contrib import messages
from django.shortcuts import redirect
from logs.mixins import LogActionMixin


class ClientCreateView(
    LoginRequiredMixin,
    GroupRequiredMixin,
    SuccessMessageMixin,
    LogActionMixin,
    CreateView,
):
    model = Client
    form_class = ClientForm
    template_name = "clients/client_form.html"
    success_url = reverse_lazy("home")
    success_message = "Клиентът беше успешно създаден."
    allowed_groups = [GROUP_BUSINESS]
    action_type = "create"

    def form_valid(self, form):
        form.instance.is_active = True
        return super().form_valid(form)

    def get_initial(self):
        initial = super().get_initial()
        eik = self.request.GET.get("eik")
        if eik:
            initial["eik"] = eik
        return initial


class ClientUpdateView(
    LoginRequiredMixin,
    GroupRequiredMixin,
    SuccessMessageMixin,
    LogActionMixin,
    UpdateView,
):
    model = Client
    form_class = ClientForm
    template_name = "clients/client_form.html"
    success_url = reverse_lazy("clients:list")
    success_message = "Данните бяха успешно редактирани."
    allowed_groups = [GROUP_BUSINESS]
    action_type = "edit"

    def form_valid(self, form):
        return super().form_valid(form)


class ClientEIKLookupView(LoginRequiredMixin, GroupRequiredMixin, View):
    template_name = "clients/client_eik_lookup.html"
    allowed_groups = [GROUP_BUSINESS]

    def get(self, request):
        form = EIKLookupForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = EIKLookupForm(request.POST)
        if form.is_valid():
            eik = form.cleaned_data["eik"]
            try:
                client = Client.objects.get(eik=eik)
                return redirect("clients:edit", pk=client.pk)
            except Client.DoesNotExist:
                messages.error(request, f"Клиент с ЕИК {eik} не съществува.")
        return render(request, self.template_name, {"form": form})


class ClientListView(
    LoginRequiredMixin,
    GroupRequiredMixin,
    PaginationMixin,
    FilterQuerysetMixin,
    ContextQueryMixin,
    ListView,
):
    model = Client
    template_name = "clients/client_list.html"
    context_object_name = "clients"
    allowed_groups = [GROUP_BUSINESS, GROUP_MANAGER, GROUP_MAKER]
    ordering = ["name"]

    def apply_filters(self, queryset):
        query = self.request.GET.get("q", "").strip()
        status = self.request.GET.get("status")
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) | Q(eik__icontains=query)
            )
        if status == "active":
            queryset = queryset.filter(is_active=True)
        elif status == "inactive":
            queryset = queryset.filter(is_active=False)
        return queryset


class ClientDeactivateView(LoginRequiredMixin, GroupRequiredMixin, View):
    allowed_groups = [GROUP_BUSINESS]

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
