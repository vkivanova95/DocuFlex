from django.urls import path
from .views import (RequestEIKSearchView, RequestFinalizeView, RequestSubmitView, AssignRequestsView,
                    AssignedRequestsListView, RequestDetailView, RequestListView, RequestDetailReadOnlyView)


urlpatterns = [
    path('add/', RequestEIKSearchView.as_view(), name='request_add'),
    path('finalize/', RequestFinalizeView.as_view(), name='request_finalize'),
    path('submit/', RequestSubmitView.as_view(), name='request_submit'),
    path('assign/', AssignRequestsView.as_view(), name='assign_requests'),
    path('assigned/', AssignedRequestsListView.as_view(), name='assigned_requests'),
    path('<int:pk>/details/', RequestDetailView.as_view(), name='request_detail'),
    path('all/', RequestListView.as_view(), name='request_list_all'),
    path('view/<int:pk>/', RequestDetailReadOnlyView.as_view(), name='request_view'),
]
