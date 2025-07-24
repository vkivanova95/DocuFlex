from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    must_change_password = models.BooleanField(default=False)
