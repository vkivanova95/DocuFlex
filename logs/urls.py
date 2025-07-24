from django.urls import path
from .views import SystemLogListView

app_name = 'logs'

urlpatterns = [
    path('', SystemLogListView.as_view(), name='log-list'),
]
