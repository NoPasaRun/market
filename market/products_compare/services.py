from dataclasses import asdict, dataclass

from django.conf import settings

from products.models import Product

try:
    from configuration_service.models import OtherSettings

    sets = OtherSettings.object.first()
    MAX_PRODS_IN_COMPARE = sets.max_prods_in_compare
except ImportError:
    MAX_PRODS_IN_COMPARE = 3


class ProductCompareList:

    def __init__(self, session):
        self.session = session
        compare_list = self.session.get(settings.PRODCOMP_SESSION_ID)
        if not compare_list:
            compare_list = self.session[settings.PRODCOMP_SESSION_ID] = []
        self.compare_list = compare_list

    def add(self, product):
        """
        Добавление товара в список сравнения
        product - модель из бд
        """
        product_id = str(product.id)
        if product_id in self.compare_list:
            return
        self.compare_list.append(product_id)
        self.save()

    def save(self):
        if len(self.compare_list) > MAX_PRODS_IN_COMPARE:
            # TODO При переполнении списка сравнения извлекаем первый или последний элемент?
            self.compare_list.pop(0)
        self.session[settings.PRODCOMP_SESSION_ID] = self.compare_list
        self.session.modified = True

    def remove(self, product):
        """
        Удаление из списка сравнения
        product - модель из бд
        """
        product_id = str(product.id)
        if product_id in self.compare_list:
            self.compare_list.pop(self.compare_list.index(product_id))
            self.save()

    def all_products(self):
        return list(Product.objects.filter(id__in=self.compare_list))

    def __iter__(self):
        products = Product.objects.filter(id__in=self.compare_list)
        for product in products.iterator():
            yield product

    def count_prods_in_compare_list(self):
        """
        Количество продуктов в списке сравнения
        """
        return len(self.compare_list)

    def clear(self):
        del self.session[settings.PRODCOMP_SESSION_ID]
        self.session.modified = True


@dataclass
class CompareRow:
    data: list
    row_type: str
    html_path: str = ""
    compare_title: str = ""
    compare_id: str = ""
    compare_uom: str = ""
    hide: bool = False


class ProductCompare:

    def __init__(self, products: list):
        self.products = products
        self._result = []

    def get_result(self):
        if not self.products:
            return self._result
        self.add_common_rows()
        self._result = self._result[:2] + self.processing() + [self._result[-1]]
        return self._result

    def processing(self) -> list:
        """
        Сбор всех видов спецификаций для данных продуктов
        Затем выборка значений спецификаций для каждого продукта
        и добавление их в self._results
        """
        return []

    def add_common_rows(self):
        for row_type in ('header', 'utils', 'rating', 'price'):
            self._result.append(asdict(CompareRow(
                data=self.products,
                row_type=row_type,
                html_path=f'products_compare/includes/{row_type}_row.html',
            )))
