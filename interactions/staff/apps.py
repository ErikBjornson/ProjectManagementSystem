from django.apps import AppConfig


class StaffConfig(AppConfig):
    """Определение конфигурации Django-приложения."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'staff'
