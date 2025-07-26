from django.db import models
from django.contrib.auth import get_user_model
from loan_requests.models import Request

class SignatureLog(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True)
    annex_number = models.CharField(max_length=100)
    sent_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50)
    response_message = models.TextField()
    file_sent = models.FileField(upload_to='sent_annexes/', null=True, blank=True)
    is_signed_successfully = models.BooleanField(default=False)
    request = models.ForeignKey(Request, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.annex_number} – {self.status}"

