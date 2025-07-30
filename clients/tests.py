from django.test import TestCase
from django.utils.timezone import now

from clients.models import Client
from contracts.models import Contract, Currency
from loan_requests.models import Request


class ClientModelTest(TestCase):
    def test_client_creation(self):
        client = Client.objects.create(name="Client1", eik="123456789")
        self.assertEqual(client.name, "Client1")
        self.assertEqual(client.eik, "123456789")


class ClientDeactivationPropagationTest(TestCase):

    def setUp(self):
        # Създаваме валутата, ако е нужна за contract
        self.currency = Currency.objects.create(
            currency_code="EUR", currency_name="Euro"
        )

    def test_deactivation_propagates(self):
        # Създаване на активен клиент
        client = Client.objects.create(name="Client1", eik="123456789", is_active=True)

        # Създаване на активен договор
        contract = Contract.objects.create(
            client=client,
            contract_number="100-123",
            start_date=now().date(),
            amount=1000,
            currency=self.currency,
            is_active=True,
        )

        # Създаване на заявка
        request = Request.objects.create(
            client=client,
            loan_agreement=contract,
            status="В процес на работа",
            amount=5000,
            currency=self.currency,
        )

        # Деактивиране на клиента
        client.is_active = False
        client.save()

        # Проверка, че договорът и заявката също са неактивни
        contract.refresh_from_db()
        request.refresh_from_db()

        self.assertFalse(
            contract.is_active,
            "Договорът трябва да е неактивен след деактивиране на клиента.",
        )
        self.assertFalse(
            request.is_active,
            "Заявката трябва да е неактивна след деактивиране на клиента.",
        )
