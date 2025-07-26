from django.db import models
from django.contrib.auth import get_user_model
from contracts.models import Contract, Currency
from clients.models import Client
from .choices import DocumentType, RequestStatus


User = get_user_model()

class Request(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    loan_agreement = models.ForeignKey(Contract, on_delete=models.CASCADE)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    document_type = models.CharField(max_length=20, choices=DocumentType.choices)
    maker = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_requests',
                              verbose_name="Изпълнител")
    preparation_date = models.DateField(null=True, blank=True)
    correction_required = models.BooleanField(null=True, blank=True)
    signing_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=RequestStatus.choices, default=RequestStatus.IN_PROGRESS)
    request_number = models.CharField(max_length=30, unique=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.request_number} – {self.status}"

    def save(self, *args, **kwargs):
        if not self.request_number:
            last_request = Request.objects.order_by('-id').first()
            if last_request and last_request.request_number and last_request.request_number.isdigit():
                new_number = int(last_request.request_number) + 1
            else:
                new_number = 1
            self.request_number = f"{new_number:04d}"

        super().save(*args, **kwargs)


