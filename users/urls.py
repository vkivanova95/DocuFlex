from django.urls import path
from .views import (
    CustomLoginView,
    ForcePasswordChangeView,
    UserCreateView,
    UserListView,
    UserEditView,
    UserDashboardView,
)
from django.contrib.auth.views import LogoutView

app_name = "users"

urlpatterns = [
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(next_page="news:welcome"), name="logout"),
    path(
        "force-password-change/",
        ForcePasswordChangeView.as_view(),
        name="force-password-change",
    ),
    path("dashboard/", UserDashboardView.as_view(), name="user-dashboard"),
    path("create/", UserCreateView.as_view(), name="user-create"),
    path("list/", UserListView.as_view(), name="user-list"),
    path("edit/<int:pk>/", UserEditView.as_view(), name="user-edit"),
]
