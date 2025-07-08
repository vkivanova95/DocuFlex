from django.urls import path
from .views import ContractCreateView, GetClientNameView, ContractEikLookupView, ContractSelectView, ContractUpdateView, \
    ContractListView, ContractDeactivateView

app_name = 'contracts'

urlpatterns = [
    path('create/', ContractCreateView.as_view(), name='create'),
    path('get-client-name/', GetClientNameView.as_view(), name='get_client_name'),
    path('edit/', ContractEikLookupView.as_view(), name='contract_eik_lookup'),
    path('select/<str:eik>/', ContractSelectView.as_view(), name='contract_select'),
    path('<int:pk>/edit/', ContractUpdateView.as_view(), name='contract_edit'),
    path('contracts/', ContractListView.as_view(), name='list'),
    path('<int:pk>/deactivate/', ContractDeactivateView.as_view(), name='deactivate'),
]