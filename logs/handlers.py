from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver
from logs.models import SystemLog
from django.utils.timezone import now


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    SystemLog.objects.create(
        user=user,
        action='login',
        model_name='Auth',
        object_id='-',
        description='User logged in.',
        timestamp=now()
    )


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    SystemLog.objects.create(
        user=user,
        action='logout',
        model_name='Auth',
        object_id='-',
        description='User logged out.',
        timestamp=now()
    )


@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    SystemLog.objects.create(
        user=None,
        action='other',
        model_name='Auth',
        object_id='-',
        description=f"Failed login attempt for username: {credentials.get('username')}",
        timestamp=now()
    )
