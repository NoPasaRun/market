from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class BrowsingHistory(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'browsing_history'
    verbose_name = _("История просмотров")
    verbose_name_plural = _("Истории просмотров")

    def ready(self):
        import browsing_history.signals  # pylint: disable=C0415, W0611
