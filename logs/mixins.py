from logs.signals import log_action


class LogActionMixin:
    action_type = None

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.action_type:
            log_action(self.request.user, self.action_type, self.object)
        return response
