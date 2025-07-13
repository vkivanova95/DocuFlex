from django.urls import path
from .views import GenerateAnnexView, AnnexArchiveView

app_name = 'annexes'

urlpatterns = [
    path('generate/', GenerateAnnexView.as_view(), name='generate_annex'),
    path('archive/', AnnexArchiveView.as_view(), name='annex_archive'),
]
