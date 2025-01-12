from django.db import models

from staff.models import Employee
from interactions.base_models import BaseModel


class Project(BaseModel):
    """Класс модели проекта, создаваемого менеджером."""

    admin = models.ForeignKey(
        verbose_name='Создатель',
        to=Employee,
        on_delete=models.CASCADE,
    )

    start_date = models.DateTimeField(
        verbose_name='Дата начала проекта',
        blank=False,
        null=True,
        default=None,
    )
    finish_date = models.DateTimeField(
        verbose_name='Дата завершения проекта',
        blank=False,
        null=True,
        default=None,
    )

    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'
        ordering = ('finish_date',)

    def __str__(self):
        """Строковое представление объекта класса Project."""
        return f'Project: {self.title}'
