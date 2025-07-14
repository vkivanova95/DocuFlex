from django.urls import path
from .views import ProductivityReportView

app_name = 'reports'

urlpatterns = [
    path('productivity/', ProductivityReportView.as_view(), name='productivity_report'),
]