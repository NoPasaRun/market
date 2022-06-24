from typing import Union

from django import template

from products.models import Product
from sellers.models import SellerProduct

register = template.Library()


@register.filter
def get_item(dictionary: dict, key):
    """
    Получение значения из словаря по ключу
    """

    return dictionary.get(key)


@register.filter
def get_old_price(product: Union[SellerProduct, Product], actual_prices: dict) -> str:
    """
    Получение цены без учёта скидок, если к товару применены скидки
    """

    if isinstance(product, SellerProduct):
        if product.price > actual_prices.get(product.pk):
            return f'$ {product.price}'
    elif average_price := getattr(product, 'average_price'):
        average_price = round(average_price, 2)
        if average_price > actual_prices.get(product.pk):
            return f'$ {round(average_price, 2)}'
    return ''


@register.filter
def get_amount_of_discount(product: Union[SellerProduct, Product], actual_prices: dict) -> str:
    """
    Расчёт размера скидки в процентах
    """

    amount_of_discount = 0
    if isinstance(product, SellerProduct):
        amount_of_discount = (product.price - actual_prices.get(product.pk)) / product.price * 100
    elif average_price := getattr(product, 'average_price'):
        amount_of_discount = (average_price - actual_prices.get(product.pk)) / average_price * 100
    return f'-{round(amount_of_discount)}%'


@register.filter
def get_display_attr_for_discount_block(product: Union[SellerProduct, Product], actual_prices: dict) -> str:
    """
    Получения значения для параметра display в зависимости от наличия скидки
    """

    if isinstance(product, SellerProduct):
        if product.price > actual_prices.get(product.pk):
            return 'flex'
    elif average_price := getattr(product, 'average_price'):
        average_price = round(average_price, 2)
        if average_price > actual_prices.get(product.pk):
            return 'flex'
    return 'none'
