from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class EyeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = "cb_backend.eye"
    verbose_name = _("Eyes")

    def ready(self):
        from cb_backend.eye import signals  # noqa
