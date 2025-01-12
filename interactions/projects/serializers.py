from typing import Optional

from rest_framework import serializers

from .models import Project
from staff.models import Employee


class BaseProjectSerializer(serializers.ModelSerializer):
    """Базовый класс сериалайзера для работы с проектами."""

    def validate_title(self, value: str) -> Optional[str]:
        """Метод валидации title (проект с таким названием ещё не создан)."""
        if Project.objects.filter(title=value).exists():
            raise serializers.ValidationError(
                "Project with this title already exists!",
            )
        return value

    def validate_admin_id(self, value: int) -> Optional[int]:
        """Метод валидации admin_id (сотрудник является администратором)."""
        if Employee.objects.get(pk=value).user_type != 'admin':
            raise serializers.ValidationError(
                "Only users with user_type='admin' can create projects!",
            )
        return value


class ProjectSerializer(BaseProjectSerializer):
    """Класс сериалайзера проекта."""

    admin_id = serializers.IntegerField()
    title = serializers.CharField(max_length=50)
    description = serializers.CharField(max_length=150)
    start_date = serializers.DateTimeField()
    finish_date = serializers.DateTimeField()

    class Meta:
        model = Project
        fields = [
            'id',
            'admin_id',
            'title',
            'description',
            'start_date',
            'finish_date',
        ]


class ProjectCreateSerializer(BaseProjectSerializer):
    """Класс сериалайзера создания нового проекта."""

    admin_id = serializers.IntegerField(write_only=True)
    title = serializers.CharField(max_length=50, write_only=True)
    description = serializers.CharField(max_length=150, write_only=True)
    start_date = serializers.DateTimeField(write_only=True, required=False)
    finish_date = serializers.DateTimeField(write_only=True, required=False)

    class Meta:
        model = Project
        fields = [
            'id',
            'admin_id',
            'title',
            'description',
            'start_date',
            'finish_date',
        ]
