import time
from threading import Thread

from django.db.models import DurationField, F
from django.db.models.functions import Cast
from django.utils import timezone

from .models import ViewedProduct


def delete_viewed_product(product: ViewedProduct):
    product.delete()


def history_deletion(update_time=30):
    while True:
        viewed_products_up_to_delete = ViewedProduct.objects.annotate(
            expire_date=Cast(timezone.now() - F("modified"),
                             output_field=DurationField())
        ).order_by("expire_date").filter(expire_date__gte=F("life"))
        threads = [Thread(target=delete_viewed_product, args=(viewed_product,))
                   for viewed_product in viewed_products_up_to_delete]
        for thread in threads:
            thread.start()
        time.sleep(update_time)
