from typing import Optional

from rest_framework import serializers

from .models import Employee


class BaseEmployeeSerializer(serializers.ModelSerializer):
    """Базовый класс сериалайзера."""

    email = serializers.EmailField(write_only=True)

    def validate_email(self, value: str) -> Optional[str]:
        """Метод валидации email (сотрудник с таким email ещё не создан)."""
        if Employee.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "An account with this email already exists!",
            )
        return value


class ExistingEmployeeSerializer(BaseEmployeeSerializer):
    """Базовый класс сериалайзера существующего аккаунта."""

    def validate_email(self, value: str) -> Optional[str]:
        """Метод валидации email (сотрудник с таким email существует)."""
        if not Employee.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "An account with this email does not exist!",
            )
        return value


class RegistrationSerializer(BaseEmployeeSerializer):
    """Класс сериалайзера регистрации сотрудника."""

    password = serializers.CharField(write_only=True)
    user_type = serializers.ChoiceField(
        write_only=True,
        choices=[
            ('admin', 'Administrator'),
            ('worker', 'Worker'),
        ],
    )
    full_name = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Employee
        fields = ['email', 'password', 'user_type', 'full_name']

    def create(self, validated_data: dict) -> Employee:
        """Метод создания и сохранения сотрудника."""
        user = Employee.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            user_type=validated_data['user_type'],
            full_name=validated_data.get('full_name'),
        )
        return user


class RegistrationVerifySerializer(BaseEmployeeSerializer):
    """Класс сериалайзера верификации регистрации сотрудника."""

    verification_code = serializers.CharField(write_only=True)

    class Meta:
        model = Employee
        fields = ['email', 'verification_code']


class LoginSerializer(ExistingEmployeeSerializer):
    """Класс сериалайзера авторизации сотрудника."""

    password = serializers.CharField(write_only=True)

    class Meta:
        model = Employee
        fields = ['email', 'password']


class PasswordRecoverySerializer(ExistingEmployeeSerializer):
    """Класс сериалайзера восстановления пароля сотрудника."""

    class Meta:
        model = Employee
        fields = ['email']


class PasswordRecoveryVerifySerializer(ExistingEmployeeSerializer):
    """Класс сериалайзера верификации при восстановлении пароля сотрудника."""

    verification_code = serializers.CharField(write_only=True)

    class Meta(PasswordRecoverySerializer.Meta):
        model = Employee
        fields = PasswordRecoverySerializer.Meta.fields + ['verification_code']


class PasswordRecoveryChangeSerializer(ExistingEmployeeSerializer):
    """Класс сериалайзера смены пароля сотрудника."""

    password = serializers.CharField(write_only=True)

    class Meta(PasswordRecoverySerializer.Meta):
        model = Employee
        fields = PasswordRecoverySerializer.Meta.fields + ['password']

    def save(self) -> Employee:
        """Метод сохранения нового пароля сотрудника."""
        user = Employee.objects.get(
            email=self.validated_data['email'],
        )

        user.set_password(self.validated_data['password'])
        user.save()

        return user


class ProfileSerializer(serializers.ModelSerializer):
    """Класс сериалайзера получения данных профиля сотрудника."""

    class Meta:
        model = Employee
        fields = ['id', 'email', 'full_name', 'user_type']


class ProfileChangeSerializer(serializers.ModelSerializer):
    """Класс сериалайзера изменения данных профиля сотрудника."""

    class Meta:
        model = Employee
        fields = ['full_name']
