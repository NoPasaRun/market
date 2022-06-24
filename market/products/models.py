from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils import Choices

SPECIFICATION_TYPES = Choices(
    ('list', _('Общая (материал, цвет)')),
    ('bool', _('Бинарная характеристика')),
    ('range', _('Характеристика из диапазона (диагональ, длинна, толщина)'))
)


class Product(models.Model):
    """
    Товар
    """

    name = models.CharField(_('наименование'), max_length=500)
    category = models.ForeignKey(
        'categories.SubCategory',
        verbose_name=_('категория'),
        related_name='products',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    image = models.ImageField(verbose_name=_('изображение'), upload_to='products/', blank=True, null=True)
    description = models.TextField(verbose_name=_('описание'), max_length=3000, blank=True)
    index = models.PositiveSmallIntegerField(verbose_name=_('индекс сортировки'), default=0)
    is_limited_edition = models.BooleanField(verbose_name=_('ограниченный тираж'), default=False)

    def return_cart_info(self) -> dict:
        return {f"product_{field}": getattr(self, field) for field in ["id", "name", "image", "description"]}

    class Meta:
        verbose_name = _('товар')
        verbose_name_plural = _('товары')
        ordering = ('-index',)

    def __str__(self):
        return f'{self.name}'

    @property
    def photo_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        return f'{settings.MEDIA_URL}no_photo.jpg'


class ProductsGroup(models.Model):
    """
    Группа товаров
    """

    name = models.CharField(_('наименование'), max_length=250)
    products = models.ManyToManyField(Product, verbose_name=_('товары'), related_name='groups', blank=True)

    class Meta:
        verbose_name = _('группа товаров')
        verbose_name_plural = _('группы товаров')
        ordering = ('id',)

    def __str__(self):
        return f'{self.name}'


class Specification(models.Model):
    """
    Характеристики товара
    """
    code = models.CharField(max_length=20, verbose_name=_('Код характеристики'), unique=True)
    categories = models.ManyToManyField("categories.SubCategory")
    title = models.CharField(max_length=200, verbose_name=_('Наименование характеристики, (и единица измерения)'))
    uom = models.CharField(max_length=20, verbose_name=_('Единица измерения'), null=True, blank=True)
    type = models.CharField(verbose_name=_('Тип характеристики'), choices=SPECIFICATION_TYPES, max_length=150)

    def __str__(self):
        return f'{self.title}'

    class Meta:
        verbose_name = _('Характеристика')
        verbose_name_plural = _('Характеристики товара')


class SpecificationValue(models.Model):
    """
    Значение характеристики
    """
    specification = models.ForeignKey(
        Specification,
        on_delete=models.CASCADE,
        verbose_name=_("Характеристика товара"),
        related_name='values'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name=_("Продукт"),
        related_name='specs'
    )
    value = models.CharField(
        max_length=250,
        blank=True,
        null=True,
        verbose_name=_("Значение характеристики")
    )

    def __str__(self):
        return f"{self.value}"

    class Meta:
        verbose_name = _('Значение характеристики')
        verbose_name_plural = _('Значения характеристик товаров')

    @property
    def get_value(self):
        if self.specification.type == 'range':
            return Decimal(self.value)
        return self.value
