import random

from django.db.models import Count, Max


def get_random_instances(model, filter_condition=None, inst_count: int = 1):
    """
    Получение случайных объектов выбранной модели

    :param model: Модель
    :param filter_condition: Условия фильтрации
    :param inst_count: Необходимое количество объектов модели

    :return: Последовательность сущностей <model>
    :rtype: [], QuerySet
    """

    qs = model.objects.filter(filter_condition) if filter_condition else model.objects.all()
    aggregation = qs.aggregate(max_id=Max('id'), count=Count('id'))
    total_instances = aggregation['count']
    if inst_count > total_instances:
        # если в БД хранится меньше записей, чем требуется -> возвращаем все
        return qs
    return random.sample(list(qs), inst_count)
