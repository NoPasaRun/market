import decimal
import itertools
from statistics import mean
from typing import Union

from django.db.models import Q, QuerySet

from discounts.consts import (BASKET_DISCOUNTS, FIX_PRICES_DISCOUNTS,
                              PERCENT_DISCOUNTS, PRODUCT_GROUP_DISCOUNTS,
                              VALUE_DISCOUNTS)
from discounts.models import Discount
from products.models import Product
from sellers.models import SellerProduct


class DiscountHandler:  # pylint: disable=R0902
    """
    Обработчик скидок

    Основные методы для работы:
    1) Получение скидок: .get_discount
    2) Получение актуальной цены: .get_actual_price
    """

    def __init__(
        self,
        products: Union[Product, SellerProduct, QuerySet[Product], QuerySet[SellerProduct]],
        products_amount: dict = None,  # {id Товара продавца: количество товара}
    ):
        self.products_amount = products_amount if products_amount else {}
        self.all_discount = False
        self.actual_prices = {}
        # определение алгоритма работы в зависимости от поступивших данных
        if isinstance(products, (Product, SellerProduct)):
            self.solo_product = True
            self.data = products
        elif products.count() > 1 or products_amount:
            self.solo_product = False
            self.data = products
        else:
            self.solo_product = True
            self.data = products.first()
        # basket_info (для расчётов групповых скидок по заказам покупателей)
        self.product_groups = set()
        self.total_price = decimal.Decimal(0)
        self.products_count = 0
        if isinstance(self.data, SellerProduct):
            self.__update_basket_info(seller_product=self.data)
        elif isinstance(self.data, QuerySet) and self.data.model is SellerProduct:
            for seller_product in self.data.all():
                self.__update_basket_info(seller_product)

    def get_discount(self, all_discount=False, group_by_product=False):
        """
        Получение актуальной скидки
        """
        self.all_discount = all_discount
        if not self.data:    # pylint: disable=R1705
            return None
        elif self.solo_product:
            result = self.get_discount_to_product()
        else:
            result = self.__get_discount_to_products()
        if not group_by_product and (
            isinstance(self.data, SellerProduct)
            or (isinstance(self.data, QuerySet) and self.data.model is SellerProduct)
        ):
            return self.__ungroup_seller_products(result)
        return result

    def get_actual_price(self):
        """
        Получение актуальной цены с учётом скидок
        """
        products_and_discounts = self.get_discount(group_by_product=True)
        if not products_and_discounts:
            return None
        self.actual_prices = {}
        if isinstance(self.data, Product) or (isinstance(self.data, QuerySet) and self.data.model is Product):
            # средняя цена по всем продавцам
            actual_average_prices = {}
            for product_id, product_info in products_and_discounts.items():
                self.__set_actual_price_for_seller_products({product_id: product_info})
                if not product_info:
                    actual_average_prices[product_id] = None
                    continue
                actual_average_prices[product_id] = self.format_price(
                    mean(list(self.actual_prices.values()))
                )
                self.actual_prices = {}
            return actual_average_prices
        self.__set_actual_price_for_seller_products(products_and_discounts)
        return self.actual_prices

    def __ungroup_seller_products(self, products_and_discounts):
        """
        Разгруппировка товаров продавцов
        """
        seller_products_and_discounts = []
        for seller_product_and_discount in products_and_discounts.values():
            seller_products_and_discounts.append(seller_product_and_discount)
        if self.solo_product:
            return seller_products_and_discounts[0]
        return seller_products_and_discounts

    def __set_actual_price_for_seller_products(self, products_and_discounts):
        """
        Заполнение self.actual_prices актуальными ценами с учётом скидок для группы товаров продавца
        """
        for product_info in products_and_discounts.values():
            for i, (seller_product, discount) in enumerate(product_info.items()):
                if seller_product.id in self.actual_prices:
                    continue
                if not discount:
                    self.actual_prices[seller_product.id] = seller_product.price
                    continue
                if i == 0 and discount.type in BASKET_DISCOUNTS:
                    return self.__calculate_actual_price_for_basket(discount, products_and_discounts)
                if discount.type in PRODUCT_GROUP_DISCOUNTS:
                    self.__calculate_actual_price_for_product_groups(discount, products_and_discounts, last_iteration=i)
                    continue
                self.actual_prices[seller_product.id] = self.format_price(
                    self.calculate_actual_price(seller_product.price, discount)
                )

    def calculate_actual_price(self, price, discount):
        """
        Расчёт актуальной цены на товар продавца с учётом скидки
        """
        if discount.type in FIX_PRICES_DISCOUNTS:
            return discount.value
        if discount.type in PERCENT_DISCOUNTS:
            return price * (1 - discount.value / decimal.Decimal(100))
        if discount.type in VALUE_DISCOUNTS:
            actual_price = price - discount.value
            return actual_price if actual_price > 1 else 1

    def __calculate_actual_price_for_basket(self, discount, products_and_discounts):
        """
        Расчёт актуальной цены на товары продавца в корзине с учётом скидки на корзину
        """
        basket_actual_price = self.calculate_actual_price(self.total_price, discount)
        discount_in_percent = 1 - (self.total_price - basket_actual_price) / self.total_price
        for product_info in products_and_discounts.values():
            for seller_product in product_info.keys():
                self.actual_prices[seller_product.id] = self.format_price(seller_product.price * discount_in_percent)

    def __calculate_actual_price_for_product_groups(self, discount, products_and_discounts, last_iteration):
        """
        Расчёт актуальной цены на товары продавца, находящиеся в группе товаров,
        на которую действует скидка на группу товаров
        """
        products_in_group = []
        total_group_price = decimal.Decimal(0)
        discount_groups_ids = discount.product_groups.values_list('pk', flat=True)
        for i, product_info in enumerate(products_and_discounts.values()):
            if i < last_iteration:
                continue
            for seller_product in product_info.keys():
                if seller_product.product.groups.filter(id__in=discount_groups_ids).exists():
                    if products_count := self.products_amount.get(str(seller_product.id)):
                        total_group_price += seller_product.price * products_count
                    else:
                        total_group_price += seller_product.price
                    products_in_group.append(seller_product)
        product_group_actual_price = self.calculate_actual_price(total_group_price, discount)
        discount_in_percent = 1 - (total_group_price - product_group_actual_price) / total_group_price
        for product in products_in_group:
            self.actual_prices[product.id] = self.format_price(product.price * discount_in_percent)

    def get_discount_to_product(self, product=None):
        """
        Скидка на отдельный товар
        """
        product = product or self.data
        if isinstance(product, Product):
            # скидка на товар по всем продавцам
            product_discount = self.get_discount_from_instance(product)
            sub_category_discount = self.get_discount_from_instance(product.category) if product.category else []
            category_discount = self.get_discount_from_instance(product.category.parent_id) if product.category else []
            seller_product_discounts = {product.id: {}}
            for seller_product in product.sellerproducts.prefetch_related('discounts'):
                seller_product_discount = self.get_discount_from_instance(seller_product)
                seller_product_discounts[product.id][seller_product] = self.__process_discounts(
                    product_discount, seller_product_discount, sub_category_discount, category_discount
                )
            return seller_product_discounts
        product_discount = self.get_discount_from_instance(product.product)
        sub_category_discount = (
            self.get_discount_from_instance(product.product.category) if product.product.category else []
        )
        category_discount = (
            self.get_discount_from_instance(product.product.category.parent_id) if product.product.category else []
        )
        return {
            product.product.id: {
                product: self.__process_discounts(
                    self.get_discount_from_instance(product),
                    product_discount,
                    sub_category_discount,
                    category_discount,
                    self.__get_basket_discounts(),
                    self.__get_products_group_discount(),
                )
            }
        }

    def __update_basket_info(self, seller_product):
        """
        Анализ списка полученных товаров для последующего поиска скидки на корзину
        """
        if amount := self.products_amount.get(str(seller_product.id)):
            self.products_count += amount
            self.total_price += seller_product.price * amount
        else:
            self.products_count += 1
            self.total_price += seller_product.price
        for group_id in seller_product.product.groups.values_list('pk', flat=True):
            self.product_groups.add(group_id)

    def __process_discounts(self, *args):
        """
        Обработка полученных скидок, в том числе и поиск приоритетной скидки
        """
        discounts = sorted(itertools.chain(*args), key=lambda discount: discount.weight)
        if self.all_discount:
            return discounts
        return discounts[-1] if discounts else None

    def get_discount_from_instance(self, instance):
        """
        Получение скидки связанной с объектом
        """
        if self.all_discount:
            return list(instance.discounts.active().order_by('weight').all())
        discount = instance.discounts.active().order_by('weight').last()
        return [discount] if discount else []

    def __get_discount_to_products(self):
        """
        Скидки на полученный перечень товаров
        """
        products_discount = {}
        for product in self.data.all():
            product_id = product.id if isinstance(product, Product) else product.product.id
            result = self.get_discount_to_product(product=product)
            if sub_dict := products_discount.get(product_id):
                sub_dict.update(result.get(product_id))
            else:
                products_discount.update(result)
        return products_discount

    def __get_basket_discounts(self):
        """
        Получение скидки на корзину
        """
        if self.all_discount:
            return []
        q = (
            (
                Q(min_products_count__lte=self.products_count)
                & Q(max_products_count__gte=self.products_count)
                & Q(min_products_price__isnull=True)
                & Q(max_products_price__isnull=True)
            )
            | (
                Q(min_products_count__isnull=True)
                & Q(max_products_count__isnull=True)
                & Q(min_products_price__lte=self.total_price)
                & Q(max_products_price__gte=self.total_price)
            )
            | (
                Q(min_products_count__lte=self.products_count)
                & Q(max_products_count__gte=self.products_count)
                & Q(min_products_price__lte=self.total_price)
                & Q(max_products_price__gte=self.total_price)
            )
        )
        basket_discounts_qs = Discount.objects.basket().filter(q).order_by('weight')
        if self.all_discount:
            return list(basket_discounts_qs.all())
        discount = basket_discounts_qs.last()
        return [discount] if discount else []

    def __get_products_group_discount(self):
        """
        Получение скидки на группу товаров
        """
        if self.all_discount:
            return []
        group_discounts_qs = Discount.objects.group().filter(product_groups__in=self.product_groups)
        active_group_discount = []
        for discount in group_discounts_qs:
            groups_ids = set(discount.product_groups.values_list('id', flat=True))
            if not groups_ids - self.product_groups:
                active_group_discount.append(discount)
        if self.all_discount:
            return active_group_discount
        group_discounts = sorted(active_group_discount, key=lambda x: x.weight)
        return [group_discounts[-1]] if group_discounts else []

    def format_price(self, price: decimal.Decimal):
        """
        Округление цен
        """
        return round(price, 2)
