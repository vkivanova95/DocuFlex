from django.test import TestCase
from django.urls import reverse_lazy
from django.contrib.auth.models import Group
from loan_requests.models import Request
from loan_requests.forms import RequestForm
from clients.models import Client, Town
from contracts.models import Contract, Currency
from users.models import CustomUser
from loan_requests.models import RequestStatus


class RequestModelAndViewTests(TestCase):
    def setUp(self):
        # Създаване на потребител
        self.business_user = CustomUser.objects.create_user(
            username="business", password="pass", email="bus@admin.com"
        )
        self.executor_user = CustomUser.objects.create_user(
            username="maker", password="pass", email="maker@admin.com"
        )

        # Обвързване с група
        business_group = Group.objects.get_or_create(name="бизнес")[0]
        self.business_user.groups.add(business_group)
        executor_group = Group.objects.get_or_create(name="изпълнител")[0]
        self.executor_user.groups.add(executor_group)

        # Номенклатури
        self.currency = Currency.objects.create(
            currency_code="EUR", currency_name="Euro"
        )
        self.town = Town.objects.create(name="София")
        self.client_obj = Client.objects.create(
            name="Test Client", eik="1234567890", is_active=True
        )

        # Договор и заявка
        self.contract = Contract.objects.create(
            client=self.client_obj,
            contract_number="100-123",
            currency=self.currency,
            start_date="2025-07-01",
            amount=5000,
            is_active=True,
        )
        self.request = Request.objects.create(
            client=self.client_obj,
            loan_agreement=self.contract,
            maker=self.business_user,
            currency=self.currency,
            amount=10000,
            status="В процес на работа",
            document_type="standard",
        )

    def test_request_default_status(self):
        req = Request.objects.create(
            client=self.client_obj,
            loan_agreement=self.contract,
            currency=self.currency,
            amount=5000,
            maker=self.business_user,
            document_type="standard",
        )
        self.assertEqual(req.status, RequestStatus.IN_PROGRESS)

    def test_request_form_invalid_without_required_fields(self):
        form = RequestForm(data={})
        self.assertFalse(form.is_valid())

    def test_submit_new_request(self):
        response = self.client.post(
            reverse_lazy("requests:request_submit"),
            {
                "client": self.client_obj.id,
                "loan_agreement": self.contract.id,
                "maker": self.business_user.id,
                "currency": self.currency.id,
                "amount": 3000,
                "document_type": "standard",
            },
        )
        self.assertEqual(response.status_code, 302)  # очакваме редирект
        self.assertEqual(Request.objects.count(), 1)

    def test_assign_request_to_executor(self):
        self.request.executor = self.executor_user
        self.request.save()
        self.assertEqual(self.request.executor.username, "executor")
