import random
import environ

from django.core.cache import cache
from django.core.mail import send_mail

env = environ.Env(
    DEBUG=(bool, False),
)

environ.Env.read_env()


def send_verification_code(email: str, verification_code: str):
    """Отправляет на указанный email код верификации."""
    send_mail(
        'TaxiUNN Verification Code',
        f'Your verification code is {verification_code}',
        f"{env('EMAIL_ADDRESS')}",
        [email],
        fail_silently=False,
    )


def make_verification_code() -> str:
    """Функция генерации пятизначного кода верификации."""
    return str(random.randint(10000, 99999))


class RegistrationCache:
    """Кеш для методов регистрации."""

    @staticmethod
    def save(email: str, code: str, data: dict):
        """Метод сохранения кода верификации и данных пользователя в кеш."""
        cache.set(f'verification_code_{email}', code, timeout=3600)
        cache.set(f'user_data_{email}', data, timeout=3600)

    @staticmethod
    def verify(email: str, code: str) -> dict | None:
        """Сранение хранимого и переданного значений."""
        stored_code = cache.get(f'verification_code_{email}')
        data = cache.get(f'user_data_{email}')
        return data if stored_code == code else None


class PasswordRecoveryCache:
    """Кеш для методов восстановления пароля."""

    @staticmethod
    def save(email: str, code: str):
        """Метод сохранения кода верификации в кеш."""
        cache.set(f'verification_code_{email}', code, timeout=3600)

    @staticmethod
    def verify(email: str, code: str) -> bool:
        """Метод валидации хранимого и переданного значений."""
        stored_code = cache.get(f'verification_code_{email}')
        is_code_valid: bool = code == stored_code
        if is_code_valid:
            cache.set(
                key=f'password_recovery_{email}',
                value=True,
                timeout=300,
            )
        return is_code_valid

    @staticmethod
    def check(email: str) -> bool:
        """Метод проверки разрешения на изменение пароля."""
        permission = cache.get(f'password_recovery_{email}')
        return bool(permission)
