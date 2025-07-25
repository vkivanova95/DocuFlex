# Generated by Django 5.2.4 on 2025-07-25 19:37

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("annexes", "0002_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="generatedannex",
            name="is_sent",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="generatedannex",
            name="send_attempts",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="generatedannex",
            name="sent_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
