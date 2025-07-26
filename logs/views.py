from django.utils.timezone import localtime
from django.views.generic import ListView

from common.mixins import PaginationMixin
from .models import SystemLog
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from common.utils import export_report_to_excel


class SystemLogListView(LoginRequiredMixin, PaginationMixin, ListView):
    model = SystemLog
    template_name = 'logs/log_list.html'
    context_object_name = 'logs'
    ordering = ['-timestamp']

    def get_queryset(self):
        queryset = SystemLog.objects.all().order_by('-timestamp')
        query = self.request.GET.get('q', '')
        if query:
            queryset = queryset.filter(
                Q(description__icontains=query) |
                Q(model_name__icontains=query) |
                Q(action__icontains=query) |
                Q(user__username__icontains=query)
            )
        return queryset

    def get(self, request, *args, **kwargs):
        if request.GET.get('export') == '1':
            queryset = self.get_queryset()

            headers = ['Дата/Час', 'Потребител', 'Действие', 'Модул', 'No', 'Описание']
            rows = [
                [
                    localtime(log.timestamp).strftime("%Y-%m-%d %H:%M:%S") if log.timestamp else '',
                    log.user.username if log.user else '',
                    log.action,
                    log.model_name,
                    log.object_id if log.object_id else '',
                    log.description
                ]
                for log in queryset
            ]
            return export_report_to_excel(headers, rows, filename='system_log_report')

        return super().get(request, *args, **kwargs)