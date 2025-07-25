# Generated by Django 5.2.4 on 2025-07-16 16:34

import clients.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Town",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        max_length=100, unique=True, verbose_name="име на града"
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name="Client",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "eik",
                    models.CharField(
                        help_text="Единен идентификационен код (само цифри).",
                        max_length=20,
                        unique=True,
                        validators=[clients.validators.validate_eik_only_digits],
                        verbose_name="ЕИК",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        max_length=255, verbose_name="Наименование на дружеството"
                    ),
                ),
                (
                    "district",
                    models.CharField(
                        blank=True, max_length=255, verbose_name="квартал"
                    ),
                ),
                (
                    "street",
                    models.CharField(blank=True, max_length=255, verbose_name="улица"),
                ),
                (
                    "number",
                    models.CharField(blank=True, max_length=10, verbose_name="номер"),
                ),
                (
                    "block",
                    models.CharField(blank=True, max_length=10, verbose_name="блок"),
                ),
                (
                    "floor",
                    models.PositiveIntegerField(
                        blank=True, null=True, verbose_name="етаж"
                    ),
                ),
                (
                    "apartment",
                    models.PositiveIntegerField(
                        blank=True, null=True, verbose_name="апартамент"
                    ),
                ),
                (
                    "represented_together",
                    models.BooleanField(
                        default=False,
                        verbose_name="Фирмата се представлява съвместно от двама",
                    ),
                ),
                (
                    "representative1",
                    models.CharField(
                        max_length=255,
                        verbose_name="Три имена на представляващия дружеството",
                    ),
                ),
                (
                    "representative2",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        verbose_name="Три имена на представляващия дружеството",
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
                (
                    "town",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="clients.town",
                        verbose_name="град",
                    ),
                ),
            ],
        ),
    ]
