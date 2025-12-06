from django.apps import AppConfig


class NewsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'news'
    verbose_name = 'News Platform'
    
    def ready(self):
        """Import admin when app is ready."""
        try:
            import news.admin  # NOQA
        except ImportError:
            pass

