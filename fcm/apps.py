from django.apps import AppConfig


class FcmConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'fcm'
    verbose_name = 'Firebase Cloud Messaging'
    
    def ready(self):
        """Import admin when app is ready."""
        try:
            import fcm.admin  # NOQA
        except ImportError:
            pass

