from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from staff.models import Employee


class ProfileTests(APITestCase):
    """Тестирование получения данных профиля менеджера."""

    def setUp(self):
        self.user = Employee.objects.create(
            email='test@test.ru',
            password='12345678',
            user_type='admin',
            full_name='Zebra Marty',
        )

        self.client.force_authenticate(user=self.user)

    def test_get_profile_data(self):
        response = self.client.get(
            path=reverse('manager_profile'),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'test@test.ru')
        self.assertEqual(response.data['full_name'], 'Zebra Marty')


class ProfileUpdateTests(APITestCase):
    """Тестирование изменения данных профиля менеджера."""

    def setUp(self):
        self.user = Employee.objects.create(
            email='test@test.ru',
            password='12345678',
            user_type='admin',
            full_name='Zebra Marty',
        )

        self.client.force_authenticate(user=self.user)

    def test_update_admin(self):
        response = self.client.put(
            path=reverse('manager_profile_change'),
            data={
                'full_name': 'Lion Alex',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['full_name'], 'Lion Alex')
