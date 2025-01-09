from django.urls import reverse
from django.core.cache import cache
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.exceptions import ErrorDetail
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Employee


class RegistrationTests(APITestCase):
    """Тестирование регистрации сотрудника."""

    def setUp(self):
        self.email = 'test@test.ru'
        self.user_type = 'admin'
        self.user_data = {
            'email': self.email,
            'password': '12345678',
            'user_type': self.user_type,
            'full_name': 'Lion Alex',
        }

    def test_successfull_registration(self):
        response = self.client.post(
            path=reverse('register'),
            data=self.user_data,
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data.get('message'),
            "You've successfully registered!",
        )

    def test_successfull_registration_no_full_name(self):
        response = self.client.post(
            path=reverse('register'),
            data={
                'email': self.email,
                'password': '12345678',
                'user_type': self.user_type,
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data.get('message'),
            "You've successfully registered!",
        )

    def test_try_registrate_registered_user(self):
        self.client.post(
            path=reverse('register'),
            data={
                'email': self.email,
                'password': '12345678',
                'user_type': self.user_type,
            },
            format='json',
        )
        response = self.client.post(
            path=reverse('register'),
            data={
                'email': self.email,
                'password': '12345678',
                'user_type': self.user_type,
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get('email')[0],
            "An account with this email already exists!",
        )

    def test_incorrect_email(self):
        response = self.client.post(
            path=reverse('register'),
            data={
                'email': f'@{self.email}',
                'password': '12345678',
                'user_type': 'admin',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get('email')[0],
            "Enter a valid email address.",
        )

    def test_incorrect_user_type(self):
        response = self.client.post(
            path=reverse('register'),
            data={
                'email': self.email,
                'password': '12345678',
                'user_type': 'boss',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get('user_type')[0],
            ErrorDetail(
                string='"boss" is not a valid choice.',
                code='invalid_choice'
            ),
        )

    def test_missing_parameters(self):
        response = self.client.post(
            path=reverse('register'),
            data={
                'email': self.email,
                'user_type': self.user_type,
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get('password')[0],
            "This field is required.",
        )


class RegistrationVerifyTests(APITestCase):
    """Тестирование верификации регистрации сотрудника."""

    def setUp(self):
        self.email = 'test@test.ru'
        self.verification_code = '76543'
        self.user_data = {
            'email': self.email,
            'password': '12345678',
            'user_type': 'admin',
        }

        cache.set(
            f'verification_code_{self.email}',
            self.verification_code,
            timeout=1000,
        )
        cache.set(
            f'user_data_{self.email}',
            self.user_data,
            timeout=1000,
        )

    def test_correct_data(self):
        response = self.client.post(
            path=reverse('activate'),
            data={
                'email': self.email,
                'verification_code': self.verification_code,
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_incorrect_data(self):
        response = self.client.post(
            path=reverse('activate'),
            data={
                'email': self.email,
                'verification_code': '78123',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginTests(APITestCase):
    """Тестирование авторизации сотрудника."""

    def setUp(self):
        self.email = 'test@test.ru'
        self.user = Employee.objects.create_user(
            email=self.email,
            password='12345678',
            user_type='admin',
        )

    def test_just_login(self):
        response = self.client.post(
            path=reverse('login'),
            data={
                'email': self.email,
                'password': '12345678',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('refresh', response.data)
        self.assertIn('access', response.data)

    def test_incorrect_password_login(self):
        response = self.client.post(
            path=reverse('login'),
            data={
                'email': self.email,
                'password': '87654321',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['password'], 'Incorrect password!')

    def test_incorrect_email_login(self):
        response = self.client.post(
            path=reverse('login'),
            data={
                'email': '',
                'password': '12345678',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_field_login(self):
        response = self.client.post(
            path=reverse('login'),
            data={
                'password': '12345678',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class RefreshTests(APITestCase):
    """Тестирование получения refresh-токена сотрудника."""

    def setUp(self):
        self.email = 'test@test.ru'
        self.user = Employee.objects.create_user(
            email=self.email,
            password='12345678',
            user_type='admin',
        )
        self.refresh_token = RefreshToken.for_user(self.user)

    def test_success_refresh(self):
        response = self.client.post(
            path=reverse('refresh'),
            data={
                'refresh_token': str(self.refresh_token),
            },
            format='json',
        )
        self.assertIn('access', response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_refresh_missing_params(self):
        response = self.client.post(
            path=reverse('refresh'),
            data={},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class PasswordRecoveryTests(APITestCase):
    """Тестирование восстановления пароля сотрудника."""

    def setUp(self):
        self.email = 'test@test.ru'
        self.user = Employee.objects.create_user(
            email='test@test.ru',
            password='12345678',
            user_type='admin',
        )

    def test_password_recovery(self):
        response = self.client.post(
            path=reverse('password_recovery'),
            data={
                'email': self.email,
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data.get('message'),
            'Check your email for the verification_code.',
        )

    def test_missing_params(self):
        response = self.client.post(
            path=reverse('password_recovery'),
            data={},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_entered_email_does_not_exist(self):
        response = self.client.post(
            path=reverse('password_recovery'),
            data={
                'email': f'test_{self.email}',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
        self.assertEqual(
            response.data.get('email'),
            [
                ErrorDetail(
                    string='An account with this email does not exist!',
                    code='invalid',
                ),
            ],
        )


class PasswordRecoveryVerifyTests(APITestCase):
    """Тестирование верификации при восстановлении пароля сотрудника."""

    def setUp(self):
        self.email = 'test@test.ru'
        self.user = Employee.objects.create_user(
            email=self.email,
            password='12345678',
            user_type='admin'
        )

        self.verification_code = '12345'
        cache.set(
            key=f'verification_code_{self.email}',
            value=self.verification_code,
            timeout=1000,
        )

    def test_password_recovery_verify(self):
        response = self.client.post(
            path=reverse('password_recovery_verify'),
            data={
                'email': self.email,
                'verification_code': self.verification_code,
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertEqual(
            response.data.get('message'),
            ['Verification was successful.'],
        )

    def test_missing_params(self):
        response = self.client.post(
            path=reverse('password_recovery_verify'),
            data={
                'email': self.email,
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('verification_code', response.data)

    def test_incorrect_email(self):
        response = self.client.post(
            path=reverse('password_recovery_verify'),
            data={
                'email': f'test_{self.email}',
                'verification_code': self.verification_code,
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_incorrect_verification_code(self):
        response = self.client.post(
            path=reverse('password_recovery_verify'),
            data={
                'email': self.email,
                'verification_code': '12344',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('verification_code', response.data)
        self.assertEqual(
            response.data.get('verification_code'),
            ['The verification code is not active.'],
        )


class PasswordRecoveryChangeTests(APITestCase):
    """Тестирование смены пароля сотрудника."""

    def setUp(self):
        self.email = 'test@test.ru'
        self.user = Employee.objects.create_user(
            email=self.email,
            password='12345678',
            user_type='admin',
        )
        cache.set(
            key=f'password_recovery_{self.email}',
            value=True,
            timeout=1000,
        )

    def test_successfull_change_password(self):
        response = self.client.post(
            path=reverse('password_recovery_change'),
            data={
                'email': self.email,
                'password': '123456789',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertEqual(
            response.data.get('message'),
            ['Password successfully changed.'],
        )

    def test_missing_params(self):
        response = self.client.post(
            path=reverse('password_recovery_change'),
            data={
                'email': self.email,
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_incorrect_email(self):
        response = self.client.post(
            path=reverse('password_recovery_change'),
            data={
                'email': f'test_{self.email}',
                'password': '123456789',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
        self.assertEqual(
            response.data.get('email'),
            [
                ErrorDetail(
                    string='An account with this email does not exist!',
                    code='invalid',
                ),
            ],
        )
