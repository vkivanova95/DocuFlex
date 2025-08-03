from django.urls import path
from .views import SendGeneratedAnnexView

app_name = "api"

urlpatterns = [
    # path("mock-sign/", MockSignAnnexView.as_view(), name="mock_sign_annex"),
    path("send-annex/<int:pk>/", SendGeneratedAnnexView.as_view(), name="send_annex"),
]
