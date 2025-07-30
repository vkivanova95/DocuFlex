from django.urls import path
from .views import ProductivityReportView, AnnexStatusReportView

app_name = "reports"

urlpatterns = [
    path("productivity/", ProductivityReportView.as_view(), name="productivity_report"),
    path(
        "annex-request-report/",
        AnnexStatusReportView.as_view(),
        name="annex_status_report",
    ),
]
