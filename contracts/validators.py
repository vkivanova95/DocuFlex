# contracts/validators.py

from django.core.exceptions import ValidationError
from clients.models import Client
from .models import Contract

# def validate_unique_contract_number(contract_number):
#     if Contract.objects.filter(contract_number=contract_number).exists():
#         raise ValidationError("Договор с този номер вече съществува.")


def validate_active_client(eik_str):
    if not Client.objects.filter(eik=eik_str, is_active=True).exists():
        raise ValidationError("Клиентът трябва да съществува и да е активен.")


