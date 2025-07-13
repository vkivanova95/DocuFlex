from django.db import models
from clients.models import Client
from contracts.models import Contract
from loan_requests.models import Request


class GeneratedAnnex(models.Model):
    request = models.ForeignKey(Request, on_delete=models.CASCADE, related_name='generated_annexes')
    annex_number = models.CharField(max_length=20)
    annex_date = models.DateField()
    file_path = models.FileField(upload_to='annexes/')
    created_at = models.DateTimeField(auto_now_add=True)

