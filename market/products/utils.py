import logging
from abc import ABC
from dataclasses import dataclass

from django.db.models import DecimalField, IntegerField, Max, Min, QuerySet
from django.db.models.functions import Cast
from django.http import QueryDict

from categories.models import SubCategory
from products.models import Specification, SpecificationValue
from sellers.models import Seller, SellerProduct

logger = logging.getLevelName(__name__)

GOOD_PARAMS = {
    'product__name': 'product__name__icontains',
}


class ParamsParser(ABC):
    """
    Базовый класс фильтра
    """
    prefix: str = None
    suffix: str = None

    def __init__(self, key: str, value: str, params=None):
        self.key = key
        self.value = value
        self.params = params

    def get_query(self) -> dict:
        """
        Запрос результата работы класса

        :return: dict ex. {'price__gt':100, 'price__lt':150}
        """
        if self._validate_key():
            return self._create_query()
        raise ValueError

    def _validate_key(self) -> bool:
        """
        Базовая проверка входящих данных

        :return: bool
        """
        if self.prefix is not None and self.prefix not in self.key:
            raise ValueError(f"Ожидается '{self.prefix}' в названии, а пришло '{self.key}'")
        if self.suffix is not None and self.suffix not in self.key:
            raise ValueError(f"Ожидается '{self.suffix}' в названии, а пришло '{self.key}'")
        return True

    def _create_query(self) -> dict:
        """
        Создает строки запросов для фильтров

        :return: dict ex. {'price__gt':100, 'price__lt':150}
        """
        raise NotImplementedError()


class CommonRangeParamsParser(ParamsParser):
    prefix: str = 'range'

    def _create_query(self):
        data = self.key.split("_")
        return {
            ''.join([data[1], '__gte']): self.value.split(";")[0],
            ''.join([data[1], '__lte']): self.value.split(";")[1],
        }


class CommonTitleParamsParser(ParamsParser):
    prefix: str = 'title'

    def _create_query(self):
        data = self.key.split("_")
        return {''.join(['product__', data[1], '__icontains']): self.value}


class CommonListParamsParser(ParamsParser):
    prefix: str = 'list'

    def _create_query(self):
        data = self.key.split("_")
        return {''.join([data[1], '__in']): self.params.getlist(self.key)}


class CommonBoolParamsParser(ParamsParser):
    prefix: str = 'bool'

    def _create_query(self):
        data = self.key.split("_")
        return {data[1]: '1' if self.value == 'on' else '0'}


class SpecificationGroupParamsParser(ParamsParser):
    prefix: str = 'group'
    suffix: str = 'spec'
    spec_query = 'product__specs__specification__code'
    spec_value_query = 'product__specs__value'

    def _create_query(self):
        spec_name, spec_query, spec_value_query = self._spec_data()
        return {
            spec_query: spec_name,
            ''.join([spec_value_query, '__in']): self.params.getlist(self.key)
        }

    def _spec_data(self) -> tuple:  # pylint: disable=E1136
        data = self.key.split("_")
        return data[1], self.spec_query, self.spec_value_query


class SpecificationListParamsParser(SpecificationGroupParamsParser):
    prefix: str = 'list'
    spec_value_query = 'product__specs__id'

    def _create_query(self):
        spec_name, spec_query, spec_value_query = self._spec_data()
        return {
            spec_query: spec_name,
            ''.join([spec_value_query, '__in']): self.params.getlist(self.key)
        }


class SpecificationBoolParamsParser(SpecificationGroupParamsParser):
    prefix: str = 'bool'

    def _create_query(self):
        spec_name, spec_query, spec_value_query = self._spec_data()
        return {
            spec_query: spec_name,
            spec_value_query: '1' if self.value == 'on' else '0'
        }


parsers = {
    'title': CommonTitleParamsParser,
    'range': CommonRangeParamsParser,
    'list': CommonListParamsParser,
    'bool': CommonBoolParamsParser,
    'group_spec': SpecificationGroupParamsParser,
    'bool_spec': SpecificationBoolParamsParser,
    'list_spec': SpecificationListParamsParser,
}


class Filter:

    def __init__(self, params: QueryDict, source_qs: QuerySet) -> None:
        self.params = params
        self.source_qs = source_qs
        self._qs: QuerySet | None = None  # pylint: disable=E1131
        self.__common_queries = {}
        self.__filter()

    def __filter(self):
        self._qs = self.source_qs
        for query in self.__check_params():
            self._qs = self._qs.filter(**query)

    @property
    def qs(self):
        return self._qs

    def get_query(self):
        return self.__common_queries

    def __check_params(self) -> list:  # pylint: disable=E1136
        queries = []
        for key, val in self.params.items():
            if not val:
                continue

            prefix, _, *suffix = key.split('_')
            parser = parsers.get('_'.join([prefix, *suffix]))
            if parser is None:
                key = GOOD_PARAMS.get(key)
                if key is not None:
                    self.__common_queries[key] = val
                continue
            obj = parser(key, val, self.params)
            if suffix == ["spec"]:
                queries.append(obj.get_query())
            else:
                self.__common_queries.update(obj.get_query())
        queries.append(self.__common_queries)
        return queries


def create_filters(all_items: QuerySet,
                   filtered_items: QuerySet,
                   params: dict = None) -> tuple:  # pylint: disable=E1136
    """
    Ищет общие для отфильтрованных товаров характеристики и добавляет их в список
    """
    common_filters = CommonFilterMaker(all_items, params)
    common_filters.run()
    main_filters = common_filters.result()

    categories = SubCategory.objects.filter(
        products__in=filtered_items.values_list('product_id', flat=True)).distinct()
    if categories.count() == 1:
        spec_filters = SpecFilterMaker(filtered_items, params)
        spec_filters.run()
        return main_filters, spec_filters.result()

    return main_filters, []


@dataclass
class RangeFilterItem:
    name_filter: str
    code: str
    min_filter: int
    max_filter: int
    min_value: int
    max_value: int
    type: str = "range"


@dataclass
class GroupFilterItem:
    name_filter: str
    code: str
    specs: QuerySet
    type: str = "group"


@dataclass
class ListFilterItem:
    name_filter: str
    code: str
    options: QuerySet
    type: str = "list"


@dataclass
class BoolFilterItem:
    name_filter: str
    code: str
    type: str = "bool"


class FilterMaker(ABC):
    """
    Абстрактный класс создания фильтров
    """
    filters_types = ('range', 'group', 'list', 'params')
    model = SellerProduct

    def __init__(self, items: QuerySet, params: dict):
        self.__result = []
        self.items = items
        self.params = params

    def run(self):
        for filter_type in self.filters_types:
            act = getattr(self, ''.join(['_', filter_type, '_filter']), None)
            if act is None or not callable(act):
                logger.info(f"Не реализован указанный тип фильтра: {filter_type}")
                continue
            self.__result.extend(act())  # pylint: disable=E1102

    def _get_queryset(self):
        return self.model.objects.all()

    def _range_filter(self) -> list:
        """
        Фильтр интервала значений
        return: list
        """
        raise NotImplementedError()

    def _list_filter(self) -> list:
        """
        Фильтр списка значений
        return: list
        """
        raise NotImplementedError()

    def _group_filter(self) -> list:
        """
        Фильтр списка значений c checkBox Input
        return: list
        """
        raise NotImplementedError()

    def result(self) -> list:
        return self.__result


class CommonFilterMaker(FilterMaker):
    """
    Класс общих фильтров на странице каталога
    (Цена, Продавец, Возможность бесплатной доставки...)
    """
    filters_types = ('range', 'list')

    # def _get_queryset(self):
    #     return self.items

    def _range_filter(self):
        qs = self._get_queryset()
        price = qs.aggregate(max_value=Cast(Max('price'), IntegerField()),
                             min_value=Cast(Min('price'), IntegerField()))
        price.update(
            {"min_filter": self.params.get('price__gte', price['min_value']),
             "max_filter": self.params.get('price__lte', price['max_value']),
             "min_value": price['min_value'],
             "max_value": price['max_value'],
             "code": "price",
             "name_filter": "Цена",
             })
        return [RangeFilterItem(**price)]

    def _list_filter(self):
        qs = self._get_queryset()
        sellers = Seller.objects.filter(sellerproducts__in=qs).distinct().select_related(
            'profile__user')
        return [ListFilterItem("Продавец", "seller", sellers)]


class SpecFilterMaker(FilterMaker):
    """
    Класс фильтров конкретной подкатегории (SubCategory)
    (диагональ, выборка цветов, наличие bluetooth...)
        # _sort_filters = ['range', 'list', 'bool', 'group']
        # Сортировка по типу характеристики
        # sorted(categories, key=lambda x: _sort_filters.index(x.type))
    """
    filters_types = ('list', 'group', 'bool')  # ('range', 'bool', 'list')

    def _get_queryset(self):
        categories = SubCategory.objects.filter(
            products__in=self.items.values_list('product_id', flat=True)).distinct()
        return Specification.objects.filter(categories=categories[0])

    def _range_filter(self):
        qs = self._get_queryset()
        qs = qs.filter(type='range')
        if not qs:
            logger.info("QS is clear")
            return []
        res = []
        for spec in qs:
            values = SpecificationValue.objects.filter(
                specification=spec).annotate(d_value=Cast('value', DecimalField())).aggregate(
                max_value=Max('d_value'), min_value=Min('d_value')
            )
            values.update(
                {"min_filter": self.params.get('value__gte', values['min_value']),
                 "max_filter": self.params.get('value__lte', values['max_value']),
                 "name_filter": spec.title, "code": spec.code}
            )
            res.append(RangeFilterItem(**values))
        return res

    def _group_filter(self):
        qs = self._get_queryset()
        qs = qs.filter(type='range')
        return [
            GroupFilterItem(
                name_filter=spec.title,
                code=spec.code + "_spec",
                specs=self._spec_filter(spec)
            ) for spec in qs
        ]

    def _spec_filter(self, spec):
        return SpecificationValue.objects.filter(
            specification=spec,
            product__in=self.items.values_list('product_id', flat=True)
        ).distinct('value')

    def _list_filter(self):
        qs = self._get_queryset()
        qs = qs.filter(type='list')
        return [
            ListFilterItem(
                name_filter=spec.title,
                code=spec.code + "_spec",
                options=self._spec_filter(spec)
            ) for spec in qs
        ]

    def _bool_filter(self):
        qs = self._get_queryset()
        qs = qs.filter(type='bool')
        return [
            BoolFilterItem(
                name_filter=spec.title,
                code=spec.code + "_spec",
            ) for spec in qs
        ]
