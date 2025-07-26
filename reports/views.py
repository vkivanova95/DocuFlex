from common.mixins import GroupRequiredMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.shortcuts import render
from django.contrib.auth import get_user_model
from loan_requests.models import Request
from annexes.models import GeneratedAnnex
from dateutil import parser
from django.utils.timezone import localtime
from common.utils import export_report_to_excel


class ProductivityReportView(LoginRequiredMixin, GroupRequiredMixin, View):
    template_name = 'reports/productivity_report.html'
    allowed_groups = ['ръководител']

    def get(self, request):
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        User = get_user_model()
        executors = User.objects.filter(groups__name='изпълнител', is_active=True)

        try:
            start = parser.parse(start_date).date() if start_date else None
            end = parser.parse(end_date).date() if end_date else None
        except (ValueError, TypeError):
            start = end = None

        requests_qs = Request.objects.all()
        annexes_qs = GeneratedAnnex.objects.all()

        if start and end:
            requests_qs = requests_qs.filter(created_at__date__range=(start, end))
            annexes_qs = annexes_qs.filter(created_at__date__range=(start, end))

        report_data = []
        for user in executors:
            user_requests = requests_qs.filter(maker=user)
            user_annexes = annexes_qs.filter(request__maker=user)

            report_data.append({
                'user': user.get_full_name() or user.username,
                'requests': user_requests.count(),
                'annexes': user_annexes.count(),
                'standard': user_annexes.filter(request__document_type='standard').count(),
                'deletion': user_annexes.filter(request__document_type='deletion').count(),
            })

        if request.GET.get("export") == "1":
            headers = ['Изпълнител', 'Брой заявки', 'Брой анекси', 'Стандартен анекс', 'Анекс за заличаване']
            rows = [[row['user'], row['requests'], row['annexes'], row['standard'], row['deletion']] for row in report_data]
            filename = f"productivity_report_{start_date}_to_{end_date}"
            return export_report_to_excel(headers, rows, filename)

        return render(request, self.template_name, {
            'report_data': report_data if start_date and end_date else [],
            'start_date': start,
            'end_date': end,
        })


class AnnexStatusReportView(LoginRequiredMixin, GroupRequiredMixin, View):
    allowed_groups = ['ръководител', 'изпълнител', 'бизнес']

    def get(self, request):
        export = request.GET.get('export')
        queryset = GeneratedAnnex.objects.select_related(
            'request__client', 'request__loan_agreement', 'request__maker'
        )

        data = []
        for annex in queryset:
            req = annex.request
            client = req.client
            contract = req.loan_agreement
            num_unsuccessful_attempts = annex.send_attempts - 1

            data.append({
                "Номер на заявка": req.request_number,
                # "Дата на заявка": localtime(req.created_at).strftime("%Y-%m-%d %H:%M:%S") if req.created_at else '',
                "Номер на договор": contract.contract_number if contract else '',
                "Номер на анекс": annex.annex_number,
                "Име на клиент": client.name if client else '',
                "ЕИК на клиент": client.eik if client else '',
                "Дата изготвяне": req.preparation_date.strftime("%Y-%m-%d") if req.preparation_date else '',
                "Корекции по анекса": "Да" if req.correction_required else "Не",
                "Дата подписване": req.signing_date.strftime("%Y-%m-%d") if req.signing_date else '',
                "Брой неуспешни опити": num_unsuccessful_attempts if annex.send_attempts > 0 else "-",
                "Изпълнител": req.maker.get_full_name() if req.maker else '',
            })

        if export == 'excel':
            headers = list(data[0].keys()) if data else []
            rows = [list(row.values()) for row in data]
            return export_report_to_excel(headers, rows, 'annex_status_report')

        return render(request, 'reports/annex_status_report.html', {'report_data': data})