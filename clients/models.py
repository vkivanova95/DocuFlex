from django.db import models
from .validators import validate_eik_only_digits


class Town(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="име на града")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Client(models.Model):
    eik = models.CharField(
        max_length=20,
        unique=True,
        validators=[validate_eik_only_digits],
        verbose_name="ЕИК",
        help_text="Единен идентификационен код (само цифри).",
    )
    name = models.CharField(max_length=255, verbose_name="Наименование на дружеството")
    town = models.ForeignKey(
        Town, on_delete=models.SET_NULL, null=True, verbose_name="град"
    )
    district = models.CharField(max_length=255, blank=True, verbose_name="квартал")
    street = models.CharField(max_length=255, blank=True, verbose_name="улица")
    number = models.CharField(max_length=10, blank=True, verbose_name="номер")
    block = models.CharField(max_length=10, blank=True, verbose_name="блок")
    floor = models.PositiveIntegerField(blank=True, null=True, verbose_name="етаж")
    apartment = models.PositiveIntegerField(
        blank=True, null=True, verbose_name="апартамент"
    )
    represented_together = models.BooleanField(
        default=False, verbose_name="Фирмата се представлява съвместно от двама"
    )
    representative1 = models.CharField(
        max_length=255, verbose_name="Три имена на представляващия дружеството"
    )
    representative2 = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Три имена на представляващия дружеството",
    )
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        is_becoming_inactive = (
            self.pk
            and self.is_active is False
            and Client.objects.get(pk=self.pk).is_active
        )

        super().save(*args, **kwargs)

        if is_becoming_inactive:
            # деактивирай договори и заявки
            self.contract_set.update(is_active=False)
            self.request_set.update(is_active=False)
            self.request_set.filter(status="in_progress").update(status="rejected")

    def __str__(self):
        return f"{self.name} ({self.eik})"
