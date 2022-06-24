from django.apps import AppConfig


class BannersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'banners'

    def ready(self):
        from banners import signals  # pylint: disable=C0415, W0611
