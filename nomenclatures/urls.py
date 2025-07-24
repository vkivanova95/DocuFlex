from django.urls import path
from .views import NomenclatureView, NomenclatureDeactivationView, CurrencyListView, LoanTypeListView, TownListView

app_name = 'nomenclatures'

urlpatterns = [
    path('', NomenclatureView.as_view(), name='nomenclature_list'),
    path('toggle/<str:model_name>/<int:pk>/', NomenclatureDeactivationView.as_view(), name='toggle-nomenclature-status'),
    path('currencies/', CurrencyListView.as_view(), name='currency_list'),
    path('loan-types/', LoanTypeListView.as_view(), name='loan_type_list'),
    path('towns/', TownListView.as_view(), name='town_list'),
]
