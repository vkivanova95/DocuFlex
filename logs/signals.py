from logs.models import SystemLog
from django.utils.timezone import now


def log_action(user, action, instance):
    model_name = instance.__class__.__name__
    object_id = str(instance.pk)
    description = f"{action.capitalize()} {model_name} with ID {object_id}"
    SystemLog.objects.create(
        user=user,
        action=action,
        model_name=model_name,
        object_id=object_id,
        description=description,
        timestamp=now()
    )
