from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import Group
from users.models import CustomUser


class AccessControlTests(TestCase):
    def setUp(self):
        self.business_user = CustomUser.objects.create_user(username='business', password='pass', email='business@example.com')
        business_group, _ = Group.objects.get_or_create(name='бизнес')
        self.business_user.groups.add(business_group)

        self.head_user = CustomUser.objects.create_user(username='head', password='pass', email='head@example.com')
        head_group, _ = Group.objects.get_or_create(name='ръководител')
        self.head_user.groups.add(head_group)

    def test_business_user_no_access_nomenclature(self):
        self.client.login(username='business', password='pass')
        response = self.client.get(reverse('nomenclatures:currency_list'))
        self.assertEqual(response.status_code, 403)

    def test_boss_user_can_access_nomenclature(self):
        self.client.login(username='head', password='pass')
        response = self.client.get(reverse('nomenclatures:currency_list'))
        self.assertEqual(response.status_code, 200)
