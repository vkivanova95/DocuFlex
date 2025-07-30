from django.db import models


class DocumentType(models.TextChoices):
    STANDARD = "standard", "Стандартен анекс"
    DELETION = "deletion", "Анекс за заличаване на обезпечение"


class RequestStatus(models.TextChoices):
    IN_PROGRESS = "in_progress", "В процес на работа"
    SIGNED = "signed", "Подписан"
    REJECTED = "rejected", "Отказан"
