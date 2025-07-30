from django.db import models
from clients.models import Client


class LoanType(models.Model):
    loan_type = models.CharField(
        max_length=50, unique=True, verbose_name="вид на кредита"
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.loan_type


class Currency(models.Model):
    currency_code = models.CharField(
        max_length=3, unique=True, verbose_name="валута код"
    )
    currency_name = models.CharField(max_length=10, verbose_name="валута име")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.currency_code


class Contract(models.Model):
    contract_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Договор номер",
        help_text="Номер на Договора за кредит.",
    )
    start_date = models.DateField(verbose_name="дата")
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, verbose_name="Клиент (ЕИК)"
    )
    loan_type = models.ForeignKey(
        LoanType,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="вид на кредита",
    )
    currency = models.ForeignKey(
        Currency,
        on_delete=models.SET_NULL,
        null=True,
        default="EUR",
        verbose_name="валута",
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.contract_number} - {self.client.name}"
