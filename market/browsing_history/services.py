from django.db.models import QuerySet

from products.models import Product

from .models import ViewedProduct


class HistoryViewService:
    def __init__(self, user):
        self.user = user
        self.model = ViewedProduct

    def add(self, add_product):
        """
        Добавление продукта в список просмотренных
        """
        if self.user.is_authenticated:
            product, _ = self.model.objects.get_or_create(product=add_product, user=self.user)
            product.save()

    def remove(self, remove_product):
        """
        Удаление продукта из списка просмотренных
        """
        product = self.model.objects.filter(product=remove_product, user=self.user)
        if product:
            product.delete()

    def count(self) -> int:
        """
        Количество просмотренных товаров
        """
        return self.model.objects.filter(user=self.user).count()

    def history_list(self, quantity=None) -> QuerySet:
        """
        Список товаров в истории просмотра
        """
        products = (
            Product.objects.with_average_price()
            .select_related('category__parent_id')
            .filter(viewed__user=self.user)
            .order_by('-viewed__updated')
        )
        return products[:quantity] if quantity else products

    def history_clear(self) -> None:
        self.model.objects.filter(user=self.user).delete()
