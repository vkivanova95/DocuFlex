from django.views.generic import ListView
from .models import SystemLog
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q


class SystemLogListView(LoginRequiredMixin, ListView):
    model = SystemLog
    template_name = 'logs/log_list.html'
    context_object_name = 'logs'
    paginate_by = 10
    ordering = ['-timestamp']

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q', '')
        if query:
            queryset = queryset.filter(
                Q(description__icontains=query) |
                Q(model_name__icontains=query) |
                Q(action__icontains=query) |
                Q(user__username__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context

    def get_paginate_by(self, queryset):
        per_page = self.request.GET.get('per_page')
        if per_page == 'all':
            return queryset.count()
        return per_page or self.paginate_by