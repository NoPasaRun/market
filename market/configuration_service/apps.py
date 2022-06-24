from django.apps import AppConfig


class ConfigurationServiceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'configuration_service'

    def ready(self):
        from .models import PeriodCash  # pylint: disable=C0415

        try:
            if not PeriodCash.objects.exists():
                PeriodCash.objects.create(
                    category_menu=60 * 60 * 24,
                    banners=60 * 10,
                    seller=60 * 60 * 24,
                    top_seller_goods=3600,
                    goods_list=3600 * 24,
                    detail_page=3600 * 24,
                    top_goods=3600 * 24,
                )
        except Exception as e:    # pylint: disable=W0703
            print(e, "Таблица не существует, скорей всего миграции еще не применены")
