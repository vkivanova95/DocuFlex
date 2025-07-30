from openpyxl import Workbook
from io import BytesIO
from django.http import HttpResponse


def export_report_to_excel(headers, rows, filename="report"):
    wb = Workbook()
    ws = wb.active
    ws.title = "Справка"

    ws.append(headers)

    for row in rows:
        ws.append(row)

    output = BytesIO()
    wb.save(output)
    output.seek(0)

    response = HttpResponse(
        output.read(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}.xlsx"'
    return response
