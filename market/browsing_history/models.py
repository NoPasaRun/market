from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel

User = get_user_model()


class ViewedProduct(TimeStampedModel):
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE,
                                related_name='viewed', verbose_name=_("Товар"))
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='viewed', verbose_name=_("Пользователь"))
    life = models.DurationField(verbose_name=_("Длительность"), default=timedelta(seconds=30),
                                help_text="Save duration in format DD HH:MM:SS.uuuuuu")

    def __str__(self):
        return f"{self.product} {self.user}"

    class Meta:
        verbose_name = _("Просмотренный товар")
        verbose_name_plural = _("Просмотренные товары")
        ordering = ('-modified',)
        unique_together = ('user', 'product')
