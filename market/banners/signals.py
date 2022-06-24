from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from banners.models import Banner


@receiver(post_save, sender=Banner)
def clean_cache_for_banner_on_save(sender, instance, **kwargs):
    cache.delete(instance.CACHE_CONSTS.get('banners'))


@receiver(post_delete, sender=Banner)
def clean_cache_for_banner_on_delete(sender, instance, **kwargs):
    cache.delete(instance.CACHE_CONSTS.get('banners'))
