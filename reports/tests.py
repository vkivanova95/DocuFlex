from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import Group
from users.models import CustomUser


class ProductivityReportExportTests(TestCase):
    def setUp(self):
        # Създаване на потребител и роля ръководител
        self.user = CustomUser.objects.create_user(
            username="manager", password="pass123", email="manager@example.com"
        )
        group, _ = Group.objects.get_or_create(name="ръководител")
        self.user.groups.add(group)
        self.client.login(username="manager", password="pass123")

    def test_export_productivity_excel(self):
        url = reverse("reports:productivity_report") + "?export=1"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response["Content-Type"],
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
