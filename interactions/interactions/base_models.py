from django.db import models


class BaseModel(models.Model):
    """Класс базовой модели для создания проектов, задач и категорий."""

    title = models.CharField(
        verbose_name='Название',
        max_length=50,
    )
    description = models.TextField(
        verbose_name='Описание',
        max_length=150,
    )

    created_at = models.DateTimeField(
        verbose_name='Дата создания',
        auto_now_add=True,
    )

    class Meta:
        abstract = True
