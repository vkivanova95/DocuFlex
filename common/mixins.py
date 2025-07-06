# common/mixins.py
from django.contrib import messages

class SuccessMessageMixin:
    success_message = None

    def form_valid(self, form):
        if self.success_message:
            messages.success(self.request, self.success_message)
        return super().form_valid(form)
