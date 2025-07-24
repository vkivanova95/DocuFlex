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


@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class SendAnnexToMockAPITest(TestCase):
    def setUp(self):
        # тестови юзър
        self.executor = CustomUser.objects.create_user(username='executor', password='pass123', email='executor@example.com')
        group = Group.objects.get_or_create(name='изпълнител')[0]
        self.executor.groups.add(group)
        self.client.login(username='executor', password='pass123')

        self.town = Town.objects.create(name='Sofia')
        self.currency = Currency.objects.create(currency_code='EUR', currency_name='Euro')
        self.client_obj = Client.objects.create(name="Test Client", eik="1234567890", is_active=True)
        self.contract = Contract.objects.create(client=self.client_obj, contract_number="C-001", currency=self.currency,
                                                start_date='2025-07-01', amount=1000, is_active=True,)
        self.request = Request.objects.create(client=self.client_obj, loan_agreement=self.contract, maker=self.executor,
                                              status='В процес на работа', currency=self.currency, amount=20000, document_type='standard')
        self.annex = GeneratedAnnex.objects.create(request=self.request, annex_number="3", annex_date="2025-07-20", file_path="dummy_path.docx",)

        # създаване на dummy file в медия папка
        self.dummy_filename = "dummy_path.docx"
        self.dummy_file_path = os.path.join(settings.MEDIA_ROOT, self.dummy_filename)
        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
        with open(self.dummy_file_path, "w") as f:
            f.write("Dummy annex content")

    def test_send_annex_to_mock_api(self):
        response = self.client.get(reverse_lazy('api:send_annex', kwargs={'pk': self.annex.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertIn('status', response.context)  # резултатит е доставен, не връща JSON

    def test_mock_sign_annex_returns_success(self):
        # ако е истинско API връща JSON, симулира входни данни
        response = self.client.post(reverse_lazy('api:mock_sign_annex'), {
            'annex_id': self.annex.pk,
            'filename': self.annex.file_path
        })
        self.annex.refresh_from_db()
        self.assertEqual(response.status_code, 200)

    def tearDown(self):
        if os.path.exists(self.dummy_file_path):
            os.remove(self.dummy_file_path)