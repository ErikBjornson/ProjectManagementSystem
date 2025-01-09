from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import BasePermission

from .models import Employee


class EmployeeJWTAuthentication(JWTAuthentication):
    """Переопределение JWT аутентификации для Employee."""

    def __init__(self, *args, **kwargs) -> None:
        """Переопределение инициализации JWTAuth для Employee."""
        super().__init__(*args, **kwargs)
        self.user_model = Employee


class IsAuthenticatedEmployee(BasePermission):
    """Проверяем, авторизован ли сотрудник."""

    def has_permission(self, request, view):
        """Проверяем, авторизован ли сотрудник."""
        if not request.user.is_authenticated:
            return False

        return (
            (isinstance(request.user, Employee) and
                request.user.is_authenticated)
        )
