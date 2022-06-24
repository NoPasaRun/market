from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SellersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sellers'
    verbose_name = _('Продавцы')

    def ready(self):
        import sellers.signals  # pylint: disable=C0415, W0611
