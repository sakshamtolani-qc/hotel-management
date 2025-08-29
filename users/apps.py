from django.apps import AppConfig
from django.db.models.signals import pre_save
from django.conf import settings


def prevent_superuser_creation(sender, instance, **kwargs):
    if settings.MODE == 'prod' and instance.is_superuser:
        raise Exception(
            "\n❌ SECURITY NOTICE: Superuser creation is disabled in development mode.\n\n"
            "For security reasons, please use one of these methods instead:\n"
            "1. Use the Django admin interface with an existing superuser account\n"
            "2. Use the API endpoints with proper authentication\n"
            "3. Set MODE=prod in your .env file if this is intended\n"
        )


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "users"

    def ready(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        pre_save.connect(prevent_superuser_creation, sender=User)
