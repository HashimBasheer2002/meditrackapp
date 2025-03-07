from django.apps import AppConfig
from django.utils.module_loading import autodiscover_modules

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        try:
            import core.signals  # Ensure signals are imported when the app is ready
        except ImportError as e:
            raise ImportError(f"Error importing signals: {e}")
