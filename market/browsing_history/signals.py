from datetime import timedelta

from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone

from .models import ViewedProduct

try:
    from configuration_service.models import OtherSettings
except ImportError:
    OtherSettings = None

DEFAULTS = dict(
    max_history_len_by_user=20,
    history_items_lifetime=30,  # days
)


@receiver(pre_save, sender=ViewedProduct)
def on_save_delete_unnecessary_objects(sender, instance, *args, **kwargs):
    """
    Добавляется life_time к инстансу что бы отслеживать даавно просмотренные товары
    пока нигде не используется, на БУДУЩЕЕ
    При сохранении нового товара в истории просмотренных товаров,
    удаляются устаревшие.
    Максимальное количество товаров в истории определяется
    настройкой "max_history_len_by_user" в сервисе конфигураций
    или константой "MAX_HISTORY_LEN_BY_USER: int = 20"
    """
    sets = get_settings_vars('max_history_len_by_user', 'history_items_lifetime')
    instance.life_time = timezone.now() + timedelta(days=sets['history_items_lifetime'])
    objects = sender.objects.filter(user=instance.user)
    if len(objects) >= sets['max_history_len_by_user']:
        for i in range(len(objects) - 1, sets['max_history_len_by_user'] - 2, -1):
            objects[i].delete()


def get_settings_vars(*args: str) -> dict:  # pylint: disable=E1136
    """
    Принимает название настроек, и пытается получить их из БД,
    если не получается, возвращает дефолтные значения
    args: str - Название настроек ( например 'max_history_len_by_user', 'history_items_lifetime')
    return: dict - Словарь принятых настроек, со значениями или None если настройка не найдена
    """
    result = dict()
    sets = DEFAULTS if OtherSettings is None else OtherSettings.object.first().__dict__

    for key in args:
        result[key] = sets.get(key)
    return result
