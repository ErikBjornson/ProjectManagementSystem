from django.db import models
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.backends import BaseBackend


class AdministratorManager(BaseUserManager):
    """Менеджер для пользователя класса Administrator."""


class Administrator(AbstractBaseUser):
    """Класс администратора."""


class AdministratorBackend(BaseBackend):
    """Класс для управления процессом аутентификации администратора."""
