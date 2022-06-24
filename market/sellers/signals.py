from django.core.cache import cache
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Seller


@receiver(post_save, sender=Seller)
def drop_seller_cache(**kwargs):
    cache.delete_many(['seller_key', 'top_products_key'])
