from tendo.singleton import SingleInstanceException
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class MassmailConfig(AppConfig):
    name = 'massmail'
    verbose_name = _("Mass mail")
    default_auto_field = 'django.db.models.AutoField'

    def ready(self):
        # Disable background threads on PythonAnywhere to prevent database timeout issues
        from webcrm.settings import ON_PYTHONANYWHERE
        if ON_PYTHONANYWHERE:
            return  # Skip starting background threads on PythonAnywhere
        
        from massmail.utils.sendmassmail import SendMassmail
        try:
            self.smm = SendMassmail()       # NOQA
            self.smm.start()
        except SingleInstanceException:
            pass
