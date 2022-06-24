from typing import Dict, List

from django.conf import settings
from django.db import transaction
from django.db.models import QuerySet

from discounts.services import DiscountHandler
from products.models import Product
from sellers.models import SellerProduct


class Cart:

    def __init__(self, session):
        self.session = session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart
        self.actual_prices = {}

    def save(self, seller_product: SellerProduct):
        """
        Сначало обновляем корзину - проверяем наличие товара в БД и
        комфликт между его кол-вом и кол-вом товара в корзине;

        Затем сохраняем в сессиях товар;

        Потом сохраняем обновленную информацию о продукте в БД;
        """
        self.update_cart()
        self.session.save()
        seller_product.save()

    def add(self, seller_product_id: int, amount: int = 1) -> None:
        product_info = self.cart.get(str(seller_product_id), False)
        seller_product: SellerProduct = SellerProduct.objects.filter(id=seller_product_id).first()
        if seller_product:
            amount = amount if seller_product.quantity-amount >= 0 else seller_product.quantity
            with transaction.atomic():
                if isinstance(product_info, dict):
                    product_info["amount"] += amount
                else:
                    self.cart[str(seller_product_id)] = {"amount": amount}
                seller_product.quantity -= amount
            self.save(seller_product)
        self.update_actual_prices()

    def remove(self, seller_product_id: int, amount: int = 1) -> None:
        product_info = self.cart.get(seller_product_id, False)
        if isinstance(product_info, dict):
            seller_product = SellerProduct.objects.filter(id=seller_product_id)
            if seller_product:
                with transaction.atomic():
                    seller_product[0].quantity += amount
                    product_info["amount"] -= amount
                self.save(seller_product[0])
            self.update_actual_prices()
        else:
            raise Exception("Can't remove product, which haven't been added to a cart!")

    def update_cart(self):
        old_cart = self.cart.copy()
        for product_id, product_info in old_cart.items():
            seller_product = SellerProduct.objects.filter(id=product_id).first()
            if not seller_product:
                self.cart.pop(product_id)
            if product_info["amount"] < 0:
                with transaction.atomic():
                    extra_amount = abs(product_info["amount"])
                    product_info["amount"] = 0
                    seller_product.quantity += extra_amount
            self.session.save()
        self.update_actual_prices()

    def serialize_data(self) -> List:
        data = []
        seller_products = SellerProduct.objects.select_related(
            "product", "seller", "seller__profile__user").defer("product__category")
        sellers = {}
        for seller_product in seller_products:
            exist = sellers.get(seller_product.product, False)
            if exist:
                sellers[seller_product.product].append(seller_product.seller)
            else:
                sellers[seller_product.product] = [seller_product.seller]
        if seller_products:
            for seller_product in self.update_actual_prices():
                updated_info = self.cart[str(seller_product.id)].copy()
                updated_info["id"] = seller_product.id

                product: Product = seller_product.product
                updated_info.update(seller_product.return_cart_info(actual_prices=self.actual_prices))
                updated_info.update(product.return_cart_info())

                updated_info.update({"sellers": sellers[product]})
                data.append(updated_info)
        return data

    def update_actual_prices(self) -> QuerySet[SellerProduct]:
        sel_ids = map(int, self.cart.keys())
        seller_products = SellerProduct.objects.select_related(None).only("id", "price").filter(id__in=sel_ids)
        products_amount = {}
        for key, info in self.cart.items():
            products_amount[key] = info["amount"]
        discount_handler = DiscountHandler(products=seller_products, products_amount=products_amount)
        self.actual_prices = discount_handler.get_actual_price()
        if self.actual_prices:
            for product_id, price in self.actual_prices.items():
                self.cart[str(product_id)].update({"price": float(price)})
        return seller_products

    def get_total_sum(self, without_discount=False) -> int:
        seller_products = self.update_actual_prices()
        if without_discount:
            return sum([self.cart[str(seller_product.id)]["amount"] * seller_product.price
                        for seller_product in seller_products])
        return sum([self.cart[str(seller_product.id)]["amount"] * self.actual_prices.get(seller_product.id)
                    for seller_product in seller_products])

    def __iter__(self) -> Dict:
        for product_id, product_info in self.cart.items():
            yield {product_id: product_info}

    def __delete__(self, instance=None) -> None:
        seller_product_ids = list(self.cart.keys())
        for seller_product_id in seller_product_ids:
            self.__delitem__(seller_product_id)
        self.session.pop(settings.CART_SESSION_ID)
        del self

    def __getitem__(self, seller_product_id: int) -> SellerProduct:
        product_info = self.cart.get(str(seller_product_id), None)
        if product_info is not None:
            seller_product = SellerProduct.objects.filter(id=seller_product_id)
            if seller_product:
                return seller_product[0]
        return None

    def __delitem__(self, seller_product_id: int) -> None:
        product_info = self.cart.get(str(seller_product_id), False)
        if product_info is not False:
            seller_product = SellerProduct.objects.filter(id=seller_product_id)
            if seller_product:
                with transaction.atomic():
                    seller_product[0].quantity += product_info["amount"]
                    self.cart.pop(str(seller_product_id))
            self.save(seller_product[0])
