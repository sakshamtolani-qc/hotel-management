# from django.apps import AppConfig


# class BillingConfig(AppConfig):
#     default_auto_field = "django.db.models.BigAutoField"
#     name = "billing"

# billing/apps.py
from django.apps import AppConfig

class BillingConfig(AppConfig):
    name = "billing"

    def ready(self):
        # import signals so they are registered
        import billing.signals  # noqa
