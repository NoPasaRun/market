from django.db import models
from django.utils.translation import gettext_lazy as _


class Banner(models.Model):
    """
    Баннер
    """

    CACHE_KEY = 'banners'

    product = models.ForeignKey(
        'products.Product', verbose_name=_('товар'), related_name='banners', on_delete=models.CASCADE
    )
    date_to = models.DateField(verbose_name=_('активен до'))
    image = models.ImageField(verbose_name=_('изображение'), upload_to='banners/')
    title = models.CharField(verbose_name=_('заголовок'), max_length=250)
    description = models.TextField(verbose_name=_('описание'), max_length=1000)
    action_name = models.CharField(verbose_name=_('надпись на кнопке'), max_length=100)

    class Meta:
        verbose_name = _('баннер')
        verbose_name_plural = _('баннеры')
        ordering = ('-date_to',)

    def __str__(self):
        return f'Баннер № {self.pk}'
