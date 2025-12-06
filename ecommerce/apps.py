from django.apps import AppConfig


class EcommerceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ecommerce'
    verbose_name = 'E-commerce Multi-Tenant'
    
    def ready(self):
        """Import admin when app is ready."""
        try:
            import ecommerce.admin  # NOQA
        except ImportError:
            pass

