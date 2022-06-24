from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _

from products.models import Product


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('пользователь'), related_name='reviews')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name=_('товар'), related_name='reviews')
    review_text = models.TextField(verbose_name=_('текст отзыва'))
    added_at = models.DateTimeField(auto_now_add=True, verbose_name=_('добавлен'))

    class Meta:
        verbose_name = _('отзыв')
        verbose_name_plural = _('отзывы')
