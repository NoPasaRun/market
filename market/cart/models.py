from django.db import models, transaction
from django.db.models.signals import post_delete
from django.dispatch.dispatcher import receiver
from django.utils.translation import gettext_lazy as _


class OrderItem(models.Model):
    seller_product = models.ForeignKey("sellers.SellerProduct", verbose_name=_("Товар продавца"),
                                       related_name="orderitems", on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(verbose_name=_("Кол-во товара"), default=0, editable=False)
    order = models.ForeignKey("Order", verbose_name=_("Заказ"), related_name="orderitems", on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        with transaction.atomic():
            self.seller_product.quantity -= self.amount
            self.seller_product.save()
            super().save(*args, **kwargs)

    def __str__(self):
        return f"Товар: <<{self.seller_product.product}>> | Заказ №_{self.order.id}"

    class Meta:
        verbose_name = _("Товар заказа")
        verbose_name_plural = _("Товары заказа")


@receiver(post_delete, sender=OrderItem)
def update_quantity_amount(sender, instance, *args, **kwargs):
    with transaction.atomic():
        instance.seller_product.quantity += instance.amount
        instance.seller_product.save()


class Order(models.Model):
    customer = models.ForeignKey("user_app.Customer", verbose_name=_("Покупатель"),
                                 related_name="orders", on_delete=models.CASCADE)
    delivery_types_choices = (
        ("express", "Экспресс доставка"),
        ("ordinary", "Обычная доставка")
    )
    payment_types_choices = (
        ("cart", "Онлайн картой"),
        ("cash", "Налом при получении"),
        ("someone-else", "Афера с чужим счетом")
    )
    status_choices = (
        ("paid", "Оплачен"),
        ("unpaid", "Не оплачен"),
        ("canceled", "Отменен")
    )
    delivery_type = models.CharField(choices=delivery_types_choices, verbose_name=_("Способ доставки"),
                                     max_length=50, default="ordinary")
    payment_type = models.CharField(choices=payment_types_choices, verbose_name=_("Способ оплаты"),
                                    max_length=50, default="cart")
    city = models.CharField(verbose_name=_("Город"), max_length=50, blank=True)
    address = models.TextField(verbose_name=_("Адрес"), max_length=200, blank=True)
    status = models.CharField(verbose_name=_("Статус"), choices=status_choices, default="unpaid", max_length=20)

    def __str__(self):
        return f"Заказ №_{self.id}"

    class Meta:
        verbose_name = _("Заказ")
        verbose_name_plural = _("Заказы")
