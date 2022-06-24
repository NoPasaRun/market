from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _


class PeriodCash(models.Model):
    category_menu = models.IntegerField(
        verbose_name=_('время кэширования меню категорий'),
        validators=[
            MinValueValidator(0),
        ],
    )
    banners = models.IntegerField(
        verbose_name=_('время кэширования баннеров'),
        validators=[
            MinValueValidator(0),
        ],
    )
    seller = models.IntegerField(
        verbose_name=_('время кэширования информации о продавцах'),
        validators=[
            MinValueValidator(0),
        ],
    )
    top_seller_goods = models.IntegerField(
        verbose_name=_('время кэширования топа товаров продавца'), validators=[MinValueValidator(0)]
    )
    goods_list = models.IntegerField(
        verbose_name=_('время кэширования списка товаров'),
        validators=[
            MinValueValidator(0),
        ],
    )
    detail_page = models.IntegerField(
        verbose_name=_('время кэширования детальной страницы'),
        validators=[
            MinValueValidator(0),
        ],
    )
    top_goods = models.IntegerField(
        verbose_name=_('время кэширования топ-товаров на главной странице'),
        validators=[
            MinValueValidator(0),
        ],
    )

    def __str__(self):
        return 'время кэширования'

    class Meta:
        verbose_name = _('время кэширования')
        verbose_name_plural = _('время кэширований')


@receiver(pre_save, sender=PeriodCash)
def check_alone_instance_period_cash(sender, instance, *args, **kwargs):
    if PeriodCash.objects.exclude(pk=instance.pk).exists():
        raise ValidationError(_('Инстанс с настройками кэширования уже существует'))
