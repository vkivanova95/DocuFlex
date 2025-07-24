from django.test import TestCase
from clients.models import Client
from contracts.models import Contract, Currency


class ContractModelTest(TestCase):
    def setUp(self):
        self.client_obj = Client.objects.create(name="Client1", eik="123456789", is_active=True)
        self.currency = Currency.objects.create(currency_code='EUR', currency_name='Euro')

    def test_contract_linked_to_client(self):
        contract = Contract.objects.create(client=self.client_obj, contract_number="100-123", currency=self.currency,
                                           start_date='2025-07-02', amount=1000, is_active=True,)
        self.assertEqual(contract.client.eik, "123456789")
        self.assertEqual(contract.currency.currency_code, 'EUR')
