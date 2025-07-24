from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import Group
from logs.models import SystemLog
from users.models import CustomUser


class LogFileViewTests(TestCase):
    def setUp(self):
        self.executor_user = CustomUser.objects.create_user(username='executor', password='pass123', email='executor@example.com')
        executor_group, _ = Group.objects.get_or_create(name='изпълнител')
        self.executor_user.groups.add(executor_group)
        self.client.login(username='executor', password='pass123')

    def test_log_filter_by_user(self):
        SystemLog.objects.create(
            user=self.executor_user,
            action='edit_request',
            model_name='Request',
            object_id='REQ-001',
            description='Промяна по заявка'
        )

        response = self.client.get(reverse('logs:log-list') + '?user=executor')
        self.assertContains(response, 'edit_request')
