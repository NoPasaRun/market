from django.utils.translation import gettext_lazy as _
from model_utils import Choices

DISCOUNT_TYPES = Choices(
    ('products_fix_price', _('фиксированная стоимость на товары')),
    ('products_percent', _('процентная скидка на товары')),
    ('products_value', _('фиксированная скидка на товары')),
    ('product_group_fix_price', _('фиксированная стоимость на наборы')),
    ('product_group_percent', _('процентная скидка на наборы')),
    ('product_group_value', _('фиксированная скидка на наборы')),
    ('category_fix_price', _('фиксированная стоимость на категорию товаров')),
    ('category_percent', _('процентная скидка на категорию товаров')),
    ('category_value', _('фиксированная скидка на категорию товаров')),
    ('basket_percent', _('процентная скидка на корзину')),
    ('basket_value', _('фиксированная скидка на корзину')),
    ('basket_fix_price', _('фиксированная стоимость на корзину')),
)

BASKET_DISCOUNTS = (
    DISCOUNT_TYPES.basket_percent,
    DISCOUNT_TYPES.basket_value,
    DISCOUNT_TYPES.basket_fix_price,
)

PRODUCT_GROUP_DISCOUNTS = (
    DISCOUNT_TYPES.product_group_fix_price,
    DISCOUNT_TYPES.product_group_percent,
    DISCOUNT_TYPES.product_group_value,
)

PRODUCT_DISCOUNTS = (
    DISCOUNT_TYPES.products_fix_price,
    DISCOUNT_TYPES.products_percent,
    DISCOUNT_TYPES.products_value,
)

CATEGORY_DISCOUNTS = (
    DISCOUNT_TYPES.category_fix_price,
    DISCOUNT_TYPES.category_percent,
    DISCOUNT_TYPES.category_value,
)

FIX_PRICES_DISCOUNTS = (
    DISCOUNT_TYPES.products_fix_price,
    DISCOUNT_TYPES.product_group_fix_price,
    DISCOUNT_TYPES.category_fix_price,
    DISCOUNT_TYPES.basket_fix_price,
)

PERCENT_DISCOUNTS = (
    DISCOUNT_TYPES.products_percent,
    DISCOUNT_TYPES.product_group_percent,
    DISCOUNT_TYPES.category_percent,
    DISCOUNT_TYPES.basket_percent,
)

VALUE_DISCOUNTS = (
    DISCOUNT_TYPES.products_value,
    DISCOUNT_TYPES.product_group_value,
    DISCOUNT_TYPES.category_value,
    DISCOUNT_TYPES.basket_value,
)
