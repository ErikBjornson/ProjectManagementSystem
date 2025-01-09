from django.db import models
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager


class EmployeeManager(BaseUserManager):
    """Менеджер для пользователя класса Employee."""

    def create_user(
        self,
        email: str,
        password: str,
        user_type: str,
        full_name: str = None,
    ):
        """Создание обычного пользователя класса Employee."""
        if not email:
            raise ValueError('Employee must have an email!')

        if not password:
            raise ValueError('Employee must have a password!')

        if not user_type:
            raise ValueError('Employee must have a user_type of user!')

        user = self.model(
            full_name=full_name,
            user_type=user_type,
            email=self.normalize_email(email),
        )
        user.set_password(password)
        user.save()

        return user

    def create_superuser(
        self,
        email: str,
        password: str,
        user_type: str,
        full_name: str = None,
    ):
        """Создание суперпользователя класса Employee."""
        user = self.create_user(email, password, user_type, full_name)
        user.make_superuser()
        user.save()

        return user


class Employee(AbstractBaseUser):
    """Класс модели сотрудника."""

    email = models.EmailField(unique=True, db_index=True)
    full_name = models.CharField(null=True, default=None)

    user_type = models.CharField(
        max_length=6,
        choices=[
            ('admin', 'Administrator'),
            ('worker', 'Worker'),
        ],
        null=False,
        default='worker',
    )

    is_active = models.BooleanField(default=True)
    is_stuff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'

    objects = EmployeeManager()

    def make_superuser(self) -> None:
        """Даёт пользователю привелегии суперпользователя."""
        self.is_stuff = True
        self.is_superuser = True

    def __str__(self):
        """Строковое представление объекта класса Employee."""
        return self.email


class EmployeeBackend(BaseBackend):
    """Класс для управления процессом аутентификации сотрудника."""

    def authenticate(self, request, email=None, password=None):
        """Метод для аутентификации."""
        try:
            user = Employee.objects.get(email=email)
        except Employee.DoesNotExist:
            return None

        if user.check_password(password):
            return user
        return None

    def get_user(self, user_id):
        """Getter пользователя."""
        try:
            return Employee.objects.get(pk=user_id)
        except Employee.DoesNotExist:
            return None
