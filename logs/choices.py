from django.db import models


class ActionType(models.TextChoices):
    CREATE = 'create', 'Create'
    EDIT = 'edit', 'Edit'
    DELETE = 'delete', 'Delete'
    LOGIN = 'login', 'Login'
    LOGOUT = 'logout', 'Logout'
    OTHER = 'other', 'Other'
