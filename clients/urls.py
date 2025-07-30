from django.urls import path
from .views import (
    ClientCreateView,
    ClientUpdateView,
    ClientEIKLookupView,
    ClientListView,
    ClientDeactivateView,
)

app_name = "clients"

urlpatterns = [
    path("eik-lookup/", ClientEIKLookupView.as_view(), name="eik_lookup"),
    path("<int:pk>/edit/", ClientUpdateView.as_view(), name="edit"),
    path("create/", ClientCreateView.as_view(), name="create"),
    path("list/", ClientListView.as_view(), name="list"),
    path("<int:pk>/deactivate/", ClientDeactivateView.as_view(), name="deactivate"),
]
