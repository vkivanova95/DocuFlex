from django.test import TestCase
from clients.models import Client


class ClientModelTest(TestCase):
    def test_client_creation(self):
        client = Client.objects.create(name="Client1", eik="123456789")
        self.assertEqual(client.name, "Test Client")
        self.assertEqual(client.eik, "123456789")
