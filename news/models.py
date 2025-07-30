from django.db import models
from django.utils import timezone


class NewsPost(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заглавие")
    content = models.TextField(verbose_name="Съдържание")
    published_at = models.DateTimeField(
        default=timezone.now, verbose_name="Дата на публикуване"
    )
    is_active = models.BooleanField(default=True, verbose_name="Активна новина")

    class Meta:
        ordering = ["-published_at"]
        verbose_name = "Новина"
        verbose_name_plural = "Новини"

    def __str__(self):
        return self.title
