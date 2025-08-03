import base64

from django.test import TestCase, override_settings
from django.urls import reverse_lazy
from django.contrib.auth.models import Group
from users.models import CustomUser
from clients.models import Client, Town
from contracts.models import Contract, Currency
from loan_requests.models import Request
from annexes.models import GeneratedAnnex
import os
from django.conf import settings
from api.views import mock_sign_annex


@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class SendAnnexToMockAPITest(TestCase):
    def setUp(self):
        # тестови юзър
        self.executor = CustomUser.objects.create_user(
            username="executor", password="pass123", email="executor@example.com"
        )
        group = Group.objects.get_or_create(name="изпълнител")[0]
        self.executor.groups.add(group)
        self.client.login(username="executor", password="pass123")

        self.town = Town.objects.create(name="Sofia")
        self.currency = Currency.objects.create(
            currency_code="EUR", currency_name="Euro"
        )
        self.client_obj = Client.objects.create(
            name="Test Client", eik="1234567890", is_active=True
        )
        self.contract = Contract.objects.create(
            client=self.client_obj,
            contract_number="C-001",
            currency=self.currency,
            start_date="2025-07-01",
            amount=1000,
            is_active=True,
        )
        self.request = Request.objects.create(
            client=self.client_obj,
            loan_agreement=self.contract,
            maker=self.executor,
            status="В процес на работа",
            currency=self.currency,
            amount=20000,
            document_type="standard",
        )
        self.annex = GeneratedAnnex.objects.create(
            request=self.request,
            annex_number="3",
            annex_date="2025-07-20",
            file_path="dummy_path.docx",
        )

        # създаване на dummy file в медия папка
        self.dummy_filename = "dummy_path.docx"
        self.dummy_file_path = os.path.join(settings.MEDIA_ROOT, self.dummy_filename)
        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
        with open(self.dummy_file_path, "w") as f:
            f.write("Dummy annex content")

    def test_mock_sign_annex_function_success(self):
        with open(self.dummy_file_path, "rb") as f:
            file_content = f.read()

        encoded = base64.b64encode(file_content).decode("utf-8")
        result = mock_sign_annex("A-1", encoded)
        self.assertIn(result["status"], ["success", "failure"])
        self.assertIn("Анекс", result["message"])

    def tearDown(self):
        if os.path.exists(self.dummy_file_path):
            os.remove(self.dummy_file_path)
