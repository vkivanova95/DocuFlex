from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()

def get_executors():
    try:
        group = Group.objects.get(name='изпълнител')
        return group.user_set.filter(is_active=True)
    except Group.DoesNotExist:
        return User.objects.none()
