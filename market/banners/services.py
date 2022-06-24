import datetime

from django.core.cache import cache
from django.db.models import Q

from banners.models import Banner
from configuration_service.models import PeriodCash
from utils.random_instances import get_random_instances


def get_banners():
    """
    Получение 3-х случайных активных баннеров из списка доступных
    """

    if not (banners := cache.get(Banner.CACHE_KEY)):
        q = Q(date_to__gte=datetime.date.today())
        banners = get_random_instances(model=Banner, filter_condition=q, inst_count=3)
        cash_settings = PeriodCash.objects.first()
        cache.set(Banner.CACHE_KEY, banners, getattr(cash_settings, Banner.CACHE_KEY))
        return banners
    return banners
