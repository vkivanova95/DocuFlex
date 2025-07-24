from django.test import TestCase
from django.urls import reverse_lazy
from annexes.forms import BaseAnnexStartForm
from annexes.models import GeneratedAnnex
from logs.models import SystemLog
from clients.models import Client, Town
from contracts.models import Contract, Currency
from users.models import CustomUser
from loan_requests.models import Request
from django.contrib.auth.models import Group


class GeneratedAnnexModelTest(TestCase):
    def setUp(self):
        self.executor = CustomUser.objects.create_user(username='executor', password='pass123', email='executor@example.com')
        executor_group = Group.objects.get_or_create(name='изпълнител')[0]
        self.executor.groups.add(executor_group)
        self.currency = Currency.objects.create(currency_code='EUR', currency_name='Euro')
        self.town = Town.objects.create(name='Sofia')
        self.client_obj = Client.objects.create(name="Client1", eik="123456789", is_active=True,)
        self.contract = Contract.objects.create(client=self.client_obj, contract_number="100-123", currency=self.currency,
                                                start_date='2025-07-02', amount=1000, is_active=True,)
        self.request = Request.objects.create(client=self.client_obj, loan_agreement=self.contract, status='В процес на работа',
                                              maker=self.executor, currency=self.currency, amount=20000, document_type='standard',)

    def test_annex_base_form_valid(self):
        data = {
            'request_number': self.request.request_number,
            'annex_number': '1',
            'annex_date': '2025-07-01',
            'city': self.town.id
        }
        form = BaseAnnexStartForm(data=data)
        self.assertTrue(form.is_valid())

    def test_generate_annex_and_log(self):
        self.client.login(username='executor', password='pass123')

        # 1 – попълване на 4те полета
        response_step1 = self.client.post(reverse_lazy('annexes:generate_annex'), {
            'request_number': self.request.request_number,
            'annex_number': 'ANX-123',
            'annex_date': '2025-07-01',
            'city': self.town.id,
        })
        self.assertEqual(response_step1.status_code, 200)
        self.assertIn('step', response_step1.context)

        # 2 – останалите
        response_step2 = self.client.post(reverse_lazy('annexes:generate_annex'), {
            'request_number': self.request.request_number,
            'annex_number': '5',
            'annex_date': '2025-07-01',
            'city': self.town.id,
            'annex_type': 'standard',
            'step': 'complete',
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '0',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'form-0-text': 'Допълнително условие 1',
        })

        self.assertEqual(response_step2.status_code, 302)
        self.assertEqual(GeneratedAnnex.objects.count(), 1)
        self.assertTrue(SystemLog.objects.filter(action='generate_annex').exists())

        log = SystemLog.objects.get(action='generate_annex')
        self.assertEqual(log.model_name, 'GeneratedAnnex')
        self.assertEqual(int(log.object_id), GeneratedAnnex.objects.first().pk)
