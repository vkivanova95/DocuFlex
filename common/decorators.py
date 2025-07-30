from django.contrib.auth.decorators import user_passes_test
from functools import wraps
from django.http import HttpResponseForbidden


def group_required(group_names):
    if isinstance(group_names, str):
        group_names = [group_names]

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if (
                request.user.is_superuser
                or request.user.groups.filter(name__in=group_names).exists()
            ):
                return view_func(request, *args, **kwargs)
            return HttpResponseForbidden("Нямате достъп до тази страница.")

        return user_passes_test(lambda u: u.is_authenticated)(_wrapped_view)

    return decorator
