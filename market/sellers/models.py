from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class Seller(models.Model):

    profile = models.OneToOneField(
        'user_app.Profile',
        null=True,
        on_delete=models.CASCADE,
        verbose_name=_('Профиль'),
        related_name='sellers'
    )
    description = models.TextField(
        verbose_name=_('Описание'),
        default=''
    )
    address = models.CharField(
        max_length=255,
        verbose_name=_('Адрес'),
        default=''
    )
    email = models.EmailField(
        verbose_name=_('Электронная почта'),
        default=''
    )

    class Meta:
        verbose_name = _('Продавец')
        verbose_name_plural = _('Продавцы')

    def __str__(self):
        return str(self.profile)

    def get_absolute_url(self):
        return reverse('sellers:seller', kwargs={'pk': self.pk})


class SellerProduct(models.Model):
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        verbose_name=_('Товар'),
        related_name='sellerproducts'
    )
    seller = models.ForeignKey(
        Seller, on_delete=models.CASCADE,
        verbose_name=_('Продавец'),
        related_name='sellerproducts'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('Цена')
    )
    quantity = models.PositiveIntegerField(
        verbose_name=_('Количество')
    )

    def return_cart_info(self, actual_prices=None) -> dict:
        actual_prices = actual_prices or {}
        info = {field: getattr(self, field) for field in ["seller", "product", "quantity"]}
        info.update(price=actual_prices.get(self.id) or self.price)
        return info

    def __str__(self):
        return f"Товар: <<{self.product}>> | Продавец: {self.seller}"

    class Meta:
        unique_together = ('product', 'seller',)
        verbose_name = _('Товар продавца')
        verbose_name_plural = _('Товары продавцов')
