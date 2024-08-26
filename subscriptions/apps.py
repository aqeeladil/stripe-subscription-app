from django.apps import AppConfig


class SubscriptionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'subscriptions'

    # Ensure you import and connect signals.py in your app's apps.py:
    def ready(self):
        import subscriptions.signals



