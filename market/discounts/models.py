from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from discounts.consts import (BASKET_DISCOUNTS, DISCOUNT_TYPES,
                              PRODUCT_GROUP_DISCOUNTS)


class DiscountsQuerySet(models.QuerySet):
    def active(self):
        date = timezone.localtime(timezone.now(), timezone.get_default_timezone()).date()
        return self.filter(date_from__lte=date, date_to__gt=date)

    def basket(self):
        return self.active().filter(type__in=BASKET_DISCOUNTS)

    def group(self):
        return self.active().filter(type__in=PRODUCT_GROUP_DISCOUNTS).prefetch_related('product_groups')


class Discount(models.Model):
    """
    Скидка
    """

    name = models.CharField(_('наименование'), max_length=250)
    description = models.TextField(verbose_name=_('описание'), max_length=2000, blank=True)
    type = models.CharField(verbose_name=_('тип'), choices=DISCOUNT_TYPES, max_length=50)
    weight = models.PositiveSmallIntegerField(verbose_name=_('вес'), default=0)
    products = models.ManyToManyField(
        'products.Product', verbose_name=_('товары'), related_name='discounts', blank=True
    )
    product_groups = models.ManyToManyField(
        'products.ProductsGroup', verbose_name=_('группы товаров'), related_name='discounts', blank=True
    )
    seller_products = models.ManyToManyField(
        'sellers.SellerProduct', verbose_name=_('товары продавцов'), related_name='discounts', blank=True
    )
    sub_categories = models.ManyToManyField(
        'categories.SubCategory', verbose_name=_('подкатегории'), related_name='discounts', blank=True
    )
    categories = models.ManyToManyField(
        'categories.Category', verbose_name=_('категории'), related_name='discounts', blank=True
    )
    value = models.DecimalField(verbose_name=_('номинал скидки'), max_digits=10, decimal_places=2)
    date_from = models.DateField(verbose_name=_('дата начала'), blank=True)
    date_to = models.DateField(verbose_name=_('дата окончания'))
    min_products_count = models.PositiveSmallIntegerField(
        verbose_name=_('минимальное количество товаров'), blank=True, null=True
    )
    max_products_count = models.PositiveSmallIntegerField(
        verbose_name=_('максимальное количество товаров'), blank=True, null=True
    )
    min_products_price = models.DecimalField(
        verbose_name=_('минимальная цена корзины'), max_digits=10, decimal_places=2, blank=True, null=True
    )
    max_products_price = models.DecimalField(
        verbose_name=_('максимальная цена корзины'), max_digits=10, decimal_places=2, blank=True, null=True
    )

    objects = DiscountsQuerySet.as_manager()

    class Meta:
        verbose_name = _('скидка')
        verbose_name_plural = _('скидки')
        ordering = ('-date_from', 'id')

    def __str__(self):
        return str(self.name)
