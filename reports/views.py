from django.shortcuts import render
from django.views import View
from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.http import HttpResponse
from openpyxl import Workbook
from io import BytesIO

from loan_requests.models import Request
from annexes.models import GeneratedAnnex

from dateutil import parser


class ProductivityReportView(View):
    template_name = 'reports/productivity_report.html'

    def get(self, request):
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        report_data = []
        User = get_user_model()
        executors = User.objects.filter(groups__name='изпълнител', is_active=True)

        # Опит за парсване на датите с dateutil
        try:
            start = parser.parse(start_date).date() if start_date else None
            end = parser.parse(end_date).date() if end_date else None
        except (ValueError, TypeError):
            start = end = None

        # Филтриране на заявките и анексите по период
        requests_qs = Request.objects.all()
        annexes_qs = GeneratedAnnex.objects.all()
        # print("Зададен период:", start, "до", end)
        # print("Общо заявки в периода:", requests_qs.count())
        # print("Общо анекси в периода:", annexes_qs.count())

        if start and end:
            requests_qs = requests_qs.filter(created_at__date__range=(start, end))
            annexes_qs = annexes_qs.filter(created_at__date__range=(start, end))



        for user in executors:
            # user_requests = requests_qs.filter(maker=user)
            # user_annexes = annexes_qs.filter(request__maker=user)
            user_requests = requests_qs.filter(maker__id=user.id)
            user_annexes = annexes_qs.filter(request__maker__id=user.id)


            report_data.append({
                'user': user.get_full_name() or user.username,
                'requests': user_requests.count(),
                'annexes': user_annexes.count(),
                'standard': user_annexes.filter(request__document_type='standard').count(),
                'deletion': user_annexes.filter(request__document_type='deletion').count(),
            })

        if not start_date or not end_date:
            report_data = []  # Празна справка, когато няма филтър

        if request.GET.get("export") == "1":
            return self.export_to_excel(report_data, start_date, end_date)

        return render(request, self.template_name, {
            'report_data': report_data,
            'start_date': start,
            'end_date': end,
        })

    def export_to_excel(self, data, start_date, end_date):
        wb = Workbook()
        ws = wb.active
        ws.title = 'Продуктивност'

        # Заглавен ред
        ws.append(['Изпълнител', 'Брой заявки', 'Брой анекси', 'Стандартен анекс', 'Анекс за заличаване'])

        for row in data:
            ws.append([
                row['user'], row['requests'], row['annexes'], row['standard'], row['deletion']
            ])

        # Запис в паметта
        output = BytesIO()
        wb.save(output)
        output.seek(0)

        # Връщане като отговор
        filename = f"productivity_report_{start_date}_to_{end_date}.xlsx"
        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
