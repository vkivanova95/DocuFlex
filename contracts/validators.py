from django.core.exceptions import ValidationError
from clients.models import Client


def validate_active_client(eik_str):
    if not Client.objects.filter(eik=eik_str, is_active=True).exists():
        raise ValidationError("Клиентът трябва да съществува и да е активен.")


