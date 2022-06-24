# pylint: skip-file
import datetime
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TransactionTestCase
from django.utils import timezone

from categories.models import Category, SubCategory
from discounts.consts import DISCOUNT_TYPES
from discounts.models import Discount
from discounts.services import DiscountHandler
from products.models import Product, ProductsGroup
from sellers.models import Seller, SellerProduct
from user_app.models import Profile


class DiscountHandlerTestCase(TransactionTestCase):
    handler = DiscountHandler

    def setUp(self):
        self.discounts, self.products, self.seller_products = {}, {}, {}
        user0 = User.objects.create(username='user1', email='user1@example.com')
        user1 = User.objects.create(username='user2', email='user2@example.com')
        profile0 = Profile.objects.create(user=user0)
        profile1 = Profile.objects.create(user=user1)
        self.seller0 = Seller.objects.create(
            profile=profile0, description='description', address='address', email='seller0@example.com'
        )
        self.seller1 = Seller.objects.create(
            profile=profile1, description='description', address='address', email='seller1@example.com'
        )
        categories, subcategories = {}, {}
        for j in range(6):
            categories[j] = Category.objects.create(name=f'категория№{j}', sort_index=0)
            for k in range(2):
                subcategories[f'{j}-{k}'] = SubCategory.objects.create(
                    name=f'{j}-{k}', parent_id=categories[j], sort_index=0
                )
                for i in range(2):
                    self.products[f'{j}-{k}-{i}'] = Product.objects.create(
                        name=f'{j}-{k}-{i}', category=subcategories[f'{j}-{k}']
                    )
                    for m in range(2):
                        self.seller_products[f'{j}-{k}-{i}-{m}'] = SellerProduct.objects.create(
                            product=self.products[f'{j}-{k}-{i}'],
                            seller=getattr(self, f'seller{m}'),
                            quantity=100,
                            price=round(Decimal(j * 100 + k * 10 + i + m / 10), 2),
                        )
        # Группы товаров
        product_group1 = ProductsGroup.objects.create(name='группа товаров №1')
        product_group1.products.add(self.products['0-0-0'])
        product_group1.products.add(self.products['0-0-1'])
        product_group2 = ProductsGroup.objects.create(name='группа товаров №2')
        product_group2.products.add(self.products['0-1-0'])
        product_group2.products.add(self.products['0-1-1'])
        product_group3 = ProductsGroup.objects.create(name='группа товаров №3')
        product_group3.products.add(self.products['1-0-0'])
        product_group3.products.add(self.products['1-0-1'])
        # Генерация товар отсутствующих в продаже
        for z in range(2):
            self.products[f'товар№{z}'] = Product.objects.create(name=f'товар№{z}')
        # Создание скидок
        # Скидки на корзину
        date = timezone.localtime(timezone.now(), timezone.get_default_timezone()).date()
        week = datetime.timedelta(days=7)
        self.discounts[DISCOUNT_TYPES.basket_percent] = Discount.objects.create(
            name=DISCOUNT_TYPES.basket_percent,
            type=DISCOUNT_TYPES.basket_percent,
            weight=1,
            value=25,
            date_from=date - week,
            date_to=date + week,
            min_products_count=2,
            max_products_count=3,
        )
        self.discounts[DISCOUNT_TYPES.basket_value] = Discount.objects.create(
            name=DISCOUNT_TYPES.basket_value,
            type=DISCOUNT_TYPES.basket_value,
            weight=2,
            value=250,
            date_from=date - week,
            date_to=date + week,
            min_products_price=600,
            max_products_price=650,
        )
        self.discounts[DISCOUNT_TYPES.basket_fix_price] = Discount.objects.create(
            name=DISCOUNT_TYPES.basket_fix_price,
            type=DISCOUNT_TYPES.basket_fix_price,
            weight=1,
            value=350,
            date_from=date - week,
            date_to=date + week,
            min_products_count=3,
            max_products_count=4,
            min_products_price=400,
            max_products_price=450,
        )
        # Скидки на наборы
        self.discounts[DISCOUNT_TYPES.product_group_percent] = Discount.objects.create(
            name=DISCOUNT_TYPES.product_group_percent,
            type=DISCOUNT_TYPES.product_group_percent,
            weight=3,
            value=35,
            date_from=date - week,
            date_to=date + week,
        )
        self.discounts[DISCOUNT_TYPES.product_group_percent].product_groups.add(product_group1)
        self.discounts[DISCOUNT_TYPES.product_group_percent].product_groups.add(product_group2)
        self.discounts[DISCOUNT_TYPES.product_group_value] = Discount.objects.create(
            name=DISCOUNT_TYPES.product_group_value,
            type=DISCOUNT_TYPES.product_group_value,
            weight=3,
            value=100,
            date_from=date - week,
            date_to=date + week,
        )
        self.discounts[DISCOUNT_TYPES.product_group_value].product_groups.add(product_group1)
        self.discounts[DISCOUNT_TYPES.product_group_value].product_groups.add(product_group3)
        self.discounts[DISCOUNT_TYPES.product_group_fix_price] = Discount.objects.create(
            name=DISCOUNT_TYPES.product_group_fix_price,
            type=DISCOUNT_TYPES.product_group_fix_price,
            weight=3,
            value=200,
            date_from=date - week,
            date_to=date + week,
        )
        self.discounts[DISCOUNT_TYPES.product_group_fix_price].product_groups.add(product_group1)
        self.discounts[DISCOUNT_TYPES.product_group_fix_price].product_groups.add(product_group2)
        self.discounts[DISCOUNT_TYPES.product_group_fix_price].product_groups.add(product_group3)
        # Скидки на товары
        self.discounts[DISCOUNT_TYPES.products_percent] = Discount.objects.create(
            name=DISCOUNT_TYPES.products_percent,
            type=DISCOUNT_TYPES.products_percent,
            weight=2,
            value=50,
            date_from=date - week,
            date_to=date + week,
        )
        self.discounts[DISCOUNT_TYPES.products_percent].products.add(self.products['2-0-0'])
        self.discounts[DISCOUNT_TYPES.products_percent].products.add(self.products['2-0-1'])
        self.discounts[DISCOUNT_TYPES.products_value] = Discount.objects.create(
            name=DISCOUNT_TYPES.products_value,
            type=DISCOUNT_TYPES.products_value,
            weight=2,
            value=50,
            date_from=date - week,
            date_to=date + week,
        )
        self.discounts[DISCOUNT_TYPES.products_value].products.add(self.products['3-1-0'])
        self.discounts[DISCOUNT_TYPES.products_value].products.add(self.products['2-1-1'])
        self.discounts[DISCOUNT_TYPES.products_fix_price] = Discount.objects.create(
            name=DISCOUNT_TYPES.products_fix_price,
            type=DISCOUNT_TYPES.products_fix_price,
            weight=3,
            value=100,
            date_from=date - week,
            date_to=date + week,
        )
        self.discounts[DISCOUNT_TYPES.products_fix_price].products.add(self.products['3-1-1'])
        self.discounts[DISCOUNT_TYPES.products_fix_price].products.add(self.products['3-0-0'])
        # Скидки на категории товаров
        self.discounts[DISCOUNT_TYPES.category_percent] = Discount.objects.create(
            name=DISCOUNT_TYPES.category_percent,
            type=DISCOUNT_TYPES.category_percent,
            weight=3,
            value=60,
            date_from=date - week,
            date_to=date + week,
        )
        self.discounts[DISCOUNT_TYPES.category_percent].sub_categories.add(subcategories['4-0'])
        self.discounts[DISCOUNT_TYPES.category_value] = Discount.objects.create(
            name=DISCOUNT_TYPES.category_value,
            type=DISCOUNT_TYPES.category_value,
            weight=2,
            value=210,
            date_from=date - week,
            date_to=date + week,
        )
        self.discounts[DISCOUNT_TYPES.category_value].categories.add(categories[4])
        self.discounts[DISCOUNT_TYPES.category_fix_price] = Discount.objects.create(
            name=DISCOUNT_TYPES.category_fix_price,
            type=DISCOUNT_TYPES.category_fix_price,
            weight=3,
            value=450.54,
            date_from=date - week,
            date_to=date + week,
        )
        self.discounts[DISCOUNT_TYPES.category_fix_price].sub_categories.add(subcategories['5-1'])
        # Прошедшая Скидка
        self.discounts[f'{DISCOUNT_TYPES.category_fix_price}_no_active'] = Discount.objects.create(
            name=DISCOUNT_TYPES.category_fix_price,
            type=DISCOUNT_TYPES.category_fix_price,
            weight=5,
            value=150,
            date_from=date - week - week,
            date_to=date - week,
        )
        self.discounts[f'{DISCOUNT_TYPES.category_fix_price}_no_active'].categories.add(categories[5])

    def test_seller_products__empty_data__get_discount(self):
        handler = self.handler(products=SellerProduct.objects.none())
        result = handler.get_discount()
        self.assertEqual(result, None)

    def test_seller_products__empty_data__get_actual_price(self):
        handler = self.handler(products=SellerProduct.objects.none())
        result = handler.get_actual_price()
        self.assertEqual(result, None)

    def test_seller_products__basket_percent__get_discount(self):
        handler = self.handler(
            products=SellerProduct.objects.filter(
                product__name__in=('1-0-0', '1-0-1', '2-1-0'), seller_id=self.seller0.id
            )
        )
        result = handler.get_discount()
        self.assertEqual(
            result,
            [
                {self.seller_products['1-0-0-0']: self.discounts[DISCOUNT_TYPES.basket_percent]},
                {self.seller_products['1-0-1-0']: self.discounts[DISCOUNT_TYPES.basket_percent]},
                {self.seller_products['2-1-0-0']: self.discounts[DISCOUNT_TYPES.basket_percent]},
            ],
        )

    def test_seller_products__basket_percent__identical_products__get_discount(self):
        handler = self.handler(
            products=SellerProduct.objects.get(product__name='1-0-1', seller_id=self.seller0.id),
            products_amount={str(self.seller_products['1-0-1-0'].id): 2},
        )
        result = handler.get_discount()
        self.assertEqual(result, {self.seller_products['1-0-1-0']: self.discounts[DISCOUNT_TYPES.basket_percent]})

    def test_seller_products__basket_percent__get_actual_price(self):
        handler = self.handler(
            products=SellerProduct.objects.filter(
                product__name__in=('1-0-0', '1-0-1', '2-1-0'), seller_id=self.seller0.id
            )
        )
        result = handler.get_actual_price()
        self.assertEqual(
            result,
            {
                self.seller_products['1-0-0-0'].id: Decimal('75.00'),
                self.seller_products['1-0-1-0'].id: Decimal('75.75'),
                self.seller_products['2-1-0-0'].id: Decimal('157.50'),
            },
        )

    def test_seller_products__basket_percent__identical_products__get_actual_price(self):
        handler = self.handler(
            products=SellerProduct.objects.get(product__name='1-0-0', seller_id=self.seller0.id),
            products_amount={str(self.seller_products['1-0-0-0'].id): 3},
        )
        result = handler.get_actual_price()
        self.assertEqual(
            result,
            {
                self.seller_products['1-0-0-0'].id: Decimal('75.00'),
            },
        )

    def test_seller_products__basket_value__get_discount(self):
        handler = self.handler(
            products=SellerProduct.objects.filter(
                product__name__in=('2-0-0', '2-1-0', '2-0-1'), seller_id=self.seller1.id
            )
        )
        result = handler.get_discount()
        self.assertEqual(
            result,
            [
                {self.seller_products['2-0-0-1']: self.discounts[DISCOUNT_TYPES.basket_value]},
                {self.seller_products['2-0-1-1']: self.discounts[DISCOUNT_TYPES.basket_value]},
                {self.seller_products['2-1-0-1']: self.discounts[DISCOUNT_TYPES.basket_value]},
            ],
        )

    def test_seller_products__basket_value__identical_products__get_discount(self):
        handler = self.handler(
            products=SellerProduct.objects.filter(product__name__in=('2-0-0', '2-0-1'), seller_id=self.seller1.id),
            products_amount={str(self.seller_products['2-0-0-1'].id): 2},
        )
        result = handler.get_discount()
        self.assertEqual(
            result,
            [
                {self.seller_products['2-0-0-1']: self.discounts[DISCOUNT_TYPES.basket_value]},
                {self.seller_products['2-0-1-1']: self.discounts[DISCOUNT_TYPES.basket_value]},
            ],
        )

    def test_seller_products__basket_value__get_actual_price(self):
        handler = self.handler(
            products=SellerProduct.objects.filter(
                product__name__in=('2-0-0', '2-1-0', '2-0-1'), seller_id=self.seller1.id
            )
        )
        result = handler.get_actual_price()
        self.assertEqual(
            result,
            {
                self.seller_products['2-0-0-1'].id: Decimal('118.27'),
                self.seller_products['2-1-0-1'].id: Decimal('124.18'),
                self.seller_products['2-0-1-1'].id: Decimal('118.86'),
            },
        )

    def test_seller_products__basket_value__identical_products__get_actual_price(self):
        handler = self.handler(
            products=SellerProduct.objects.filter(product__name__in=('2-1-0', '2-0-1'), seller_id=self.seller1.id),
            products_amount={str(self.seller_products['2-1-0-1'].id): 2},
        )
        result = handler.get_actual_price()
        self.assertEqual(
            result,
            {
                self.seller_products['2-1-0-1'].id: Decimal('125.56'),
                self.seller_products['2-0-1-1'].id: Decimal('120.18'),
            },
        )

    def test_seller_products__basket_fix_price__get_discount(self):
        handler = self.handler(
            products=SellerProduct.objects.filter(
                product__name__in=('1-0-0', '1-0-1', '1-1-0', '1-1-1'), seller_id=self.seller0.id
            )
        )
        result = handler.get_discount()
        self.assertEqual(
            result,
            [
                {self.seller_products['1-0-0-0']: self.discounts[DISCOUNT_TYPES.basket_fix_price]},
                {self.seller_products['1-0-1-0']: self.discounts[DISCOUNT_TYPES.basket_fix_price]},
                {self.seller_products['1-1-0-0']: self.discounts[DISCOUNT_TYPES.basket_fix_price]},
                {self.seller_products['1-1-1-0']: self.discounts[DISCOUNT_TYPES.basket_fix_price]},
            ],
        )

    def test_seller_products__basket_fix_price__identical_products__get_discount(self):
        handler = self.handler(
            products=SellerProduct.objects.filter(product__name__in=('1-0-0', '1-1-1'), seller_id=self.seller0.id),
            products_amount={str(self.seller_products['1-0-0-0'].id): 2, str(self.seller_products['1-1-1-0'].id): 2},
        )
        result = handler.get_discount()
        self.assertEqual(
            result,
            [
                {self.seller_products['1-0-0-0']: self.discounts[DISCOUNT_TYPES.basket_fix_price]},
                {self.seller_products['1-1-1-0']: self.discounts[DISCOUNT_TYPES.basket_fix_price]},
            ],
        )

    def test_seller_products__basket_fix_price__get_actual_price(self):
        handler = self.handler(
            products=SellerProduct.objects.filter(
                product__name__in=('1-0-0', '1-0-1', '1-1-0', '1-1-1'), seller_id=self.seller0.id
            )
        )
        result = handler.get_actual_price()
        self.assertEqual(
            result,
            {
                self.seller_products['1-0-0-0'].id: Decimal('82.94'),
                self.seller_products['1-0-1-0'].id: Decimal('83.77'),
                self.seller_products['1-1-0-0'].id: Decimal('91.23'),
                self.seller_products['1-1-1-0'].id: Decimal('92.06'),
            },
        )

    def test_seller_products__basket_fix_price__identical_products__get_actual_price(self):
        handler = self.handler(
            products=SellerProduct.objects.filter(product__name__in=('1-1-0', '1-1-1'), seller_id=self.seller0.id),
            products_amount={str(self.seller_products['1-1-0-0'].id): 3},
        )
        result = handler.get_actual_price()
        self.assertEqual(
            result,
            {
                self.seller_products['1-1-0-0'].id: Decimal('87.30'),
                self.seller_products['1-1-1-0'].id: Decimal('88.10'),
            },
        )

    def test_seller_products__product_group_percent__get_discount(self):
        handler = self.handler(
            products=SellerProduct.objects.filter(product__name__in=('0-0-1', '0-1-1'), seller_id=self.seller1.id)
        )
        result = handler.get_discount()
        self.assertEqual(
            result,
            [
                {self.seller_products['0-0-1-1']: self.discounts[DISCOUNT_TYPES.product_group_percent]},
                {self.seller_products['0-1-1-1']: self.discounts[DISCOUNT_TYPES.product_group_percent]},
            ],
        )

    def test_seller_products__product_group_percent__identical_products__get_discount(self):
        handler = self.handler(
            products=SellerProduct.objects.filter(product__name__in=('0-0-1', '0-1-1'), seller_id=self.seller1.id),
            products_amount={str(self.seller_products['0-0-1-1'].id): 10, str(self.seller_products['0-1-1-1'].id): 3},
        )
        result = handler.get_discount()
        self.assertEqual(
            result,
            [
                {self.seller_products['0-0-1-1']: self.discounts[DISCOUNT_TYPES.product_group_percent]},
                {self.seller_products['0-1-1-1']: self.discounts[DISCOUNT_TYPES.product_group_percent]},
            ],
        )

    def test_seller_products__product_group_percent__get_actual_price(self):
        handler = self.handler(
            products=SellerProduct.objects.filter(
                product__name__in=('0-0-1', '0-1-0', '0-1-1'), seller_id=self.seller1.id
            )
        )
        result = handler.get_actual_price()
        self.assertEqual(
            result,
            {
                self.seller_products['0-0-1-1'].id: Decimal('0.72'),
                self.seller_products['0-1-0-1'].id: Decimal('6.56'),
                self.seller_products['0-1-1-1'].id: Decimal('7.22'),
            },
        )

    def test_seller_products__product_group_percent__identical_products__get_actual_price(self):
        handler = self.handler(
            products=SellerProduct.objects.filter(
                product__name__in=('0-0-1', '0-1-0', '0-1-1'), seller_id=self.seller1.id
            ),
            products_amount={str(self.seller_products['0-0-1-1'].id): 10, str(self.seller_products['0-1-1-1'].id): 3},
        )
        result = handler.get_actual_price()
        self.assertEqual(
            result,
            {
                self.seller_products['0-0-1-1'].id: Decimal('0.72'),
                self.seller_products['0-1-0-1'].id: Decimal('6.56'),
                self.seller_products['0-1-1-1'].id: Decimal('7.22'),
            },
        )

    def test_seller_products__product_group_value__get_discount(self):
        handler = self.handler(
            products=SellerProduct.objects.filter(
                product__name__in=('0-0-0', '0-0-1', '1-0-0', '1-0-1'), seller_id=self.seller1.id
            )
        )
        result = handler.get_discount()
        self.assertEqual(
            result,
            [
                {self.seller_products['0-0-0-1']: self.discounts[DISCOUNT_TYPES.product_group_value]},
                {self.seller_products['0-0-1-1']: self.discounts[DISCOUNT_TYPES.product_group_value]},
                {self.seller_products['1-0-0-1']: self.discounts[DISCOUNT_TYPES.product_group_value]},
                {self.seller_products['1-0-1-1']: self.discounts[DISCOUNT_TYPES.product_group_value]},
            ],
        )

    def test_seller_products__product_group_value__identical_products__get_discount(self):
        handler = self.handler(
            products=SellerProduct.objects.filter(
                product__name__in=('0-0-0', '0-0-1', '1-0-0', '1-0-1'), seller_id=self.seller1.id
            ),
            products_amount={
                str(self.seller_products['0-0-0-1'].id): 10,
                str(self.seller_products['0-0-1-1'].id): 3,
                str(self.seller_products['1-0-1-1'].id): 7,
            },
        )
        result = handler.get_discount()
        self.assertEqual(
            result,
            [
                {self.seller_products['0-0-0-1']: self.discounts[DISCOUNT_TYPES.product_group_value]},
                {self.seller_products['0-0-1-1']: self.discounts[DISCOUNT_TYPES.product_group_value]},
                {self.seller_products['1-0-0-1']: self.discounts[DISCOUNT_TYPES.product_group_value]},
                {self.seller_products['1-0-1-1']: self.discounts[DISCOUNT_TYPES.product_group_value]},
            ],
        )

    def test_seller_products__product_group_value__get_actual_price(self):
        handler = self.handler(
            products=SellerProduct.objects.filter(
                product__name__in=('0-0-1', '1-0-0', '1-0-1'), seller_id=self.seller1.id
            )
        )
        result = handler.get_actual_price()
        self.assertEqual(
            result,
            {
                self.seller_products['0-0-1-1'].id: Decimal('0.56'),
                self.seller_products['1-0-0-1'].id: Decimal('50.62'),
                self.seller_products['1-0-1-1'].id: Decimal('51.12'),
            },
        )

    def test_seller_products__product_group_value__identical_products__get_actual_price(self):
        handler = self.handler(
            products=SellerProduct.objects.filter(
                product__name__in=('0-0-1', '1-0-0', '1-0-1'), seller_id=self.seller1.id
            ),
            products_amount={
                str(self.seller_products['0-0-1-1'].id): 2,
                str(self.seller_products['1-0-0-1'].id): 3,
                str(self.seller_products['1-0-1-1'].id): 4,
            },
        )
        result = handler.get_actual_price()
        self.assertEqual(
            result,
            {
                self.seller_products['0-0-1-1'].id: Decimal('0.94'),
                self.seller_products['1-0-0-1'].id: Decimal('85.94'),
                self.seller_products['1-0-1-1'].id: Decimal('86.80'),
            },
        )

    def test_seller_products__product_group_fix_price__get_discount(self):
        handler = self.handler(
            products=SellerProduct.objects.filter(
                product__name__in=('0-0-1', '0-1-0', '0-1-1', '1-0-0', '1-0-1'), seller_id=self.seller0.id
            )
        )
        result = handler.get_discount()
        self.assertEqual(
            result,
            [
                {self.seller_products['0-0-1-0']: self.discounts[DISCOUNT_TYPES.product_group_fix_price]},
                {self.seller_products['0-1-0-0']: self.discounts[DISCOUNT_TYPES.product_group_fix_price]},
                {self.seller_products['0-1-1-0']: self.discounts[DISCOUNT_TYPES.product_group_fix_price]},
                {self.seller_products['1-0-0-0']: self.discounts[DISCOUNT_TYPES.product_group_fix_price]},
                {self.seller_products['1-0-1-0']: self.discounts[DISCOUNT_TYPES.product_group_fix_price]},
            ],
        )

    def test_seller_products__product_group_fix_price__identical_products__get_discount(self):
        handler = self.handler(
            products=SellerProduct.objects.filter(
                product__name__in=('0-0-1', '0-1-0', '0-1-1', '1-0-0', '1-0-1'), seller_id=self.seller0.id
            ),
            products_amount={str(self.seller_products['0-0-1-0'].id): 10, str(self.seller_products['0-1-1-1'].id): 3},
        )
        result = handler.get_discount()
        self.assertEqual(
            result,
            [
                {self.seller_products['0-0-1-0']: self.discounts[DISCOUNT_TYPES.product_group_fix_price]},
                {self.seller_products['0-1-0-0']: self.discounts[DISCOUNT_TYPES.product_group_fix_price]},
                {self.seller_products['0-1-1-0']: self.discounts[DISCOUNT_TYPES.product_group_fix_price]},
                {self.seller_products['1-0-0-0']: self.discounts[DISCOUNT_TYPES.product_group_fix_price]},
                {self.seller_products['1-0-1-0']: self.discounts[DISCOUNT_TYPES.product_group_fix_price]},
            ],
        )

    def test_seller_products__product_group_fix_price__get_actual_price(self):
        handler = self.handler(
            products=SellerProduct.objects.filter(
                product__name__in=('0-0-1', '0-1-0', '0-1-1', '1-0-0', '1-0-1'), seller_id=self.seller0.id
            )
        )
        result = handler.get_actual_price()
        self.assertEqual(
            result,
            {
                self.seller_products['0-0-1-0'].id: Decimal('0.90'),
                self.seller_products['0-1-0-0'].id: Decimal('8.97'),
                self.seller_products['0-1-1-0'].id: Decimal('9.87'),
                self.seller_products['1-0-0-0'].id: Decimal('89.69'),
                self.seller_products['1-0-1-0'].id: Decimal('90.58'),
            },
        )

    def test_seller_products__product_group_fix_price__identical_products__get_actual_price(self):
        handler = self.handler(
            products=SellerProduct.objects.filter(
                product__name__in=('0-0-1', '0-1-0', '0-1-1', '1-0-0', '1-0-1'), seller_id=self.seller0.id
            ),
            products_amount={
                str(self.seller_products['0-0-1-0'].id): 6,
                str(self.seller_products['0-1-0-0'].id): 3,
                str(self.seller_products['0-1-1-0'].id): 4,
                str(self.seller_products['1-0-0-0'].id): 5,
            },
        )
        result = handler.get_actual_price()
        self.assertEqual(
            result,
            {
                self.seller_products['0-0-1-0'].id: Decimal('0.29'),
                self.seller_products['0-1-0-0'].id: Decimal('2.94'),
                self.seller_products['0-1-1-0'].id: Decimal('3.23'),
                self.seller_products['1-0-0-0'].id: Decimal('29.37'),
                self.seller_products['1-0-1-0'].id: Decimal('29.66'),
            },
        )

    def test_seller_products__products_percent__get_discount(self):
        handler = self.handler(
            products=SellerProduct.objects.filter(product__name__in=('2-0-0', '2-0-1'), seller_id=self.seller1.id)
        )
        result = handler.get_discount()
        self.assertEqual(
            result,
            [
                {self.seller_products['2-0-0-1']: self.discounts[DISCOUNT_TYPES.products_percent]},
                {self.seller_products['2-0-1-1']: self.discounts[DISCOUNT_TYPES.products_percent]},
            ],
        )

    def test_seller_products__products_percent__get_actual_price(self):
        handler = self.handler(
            products=SellerProduct.objects.filter(product__name__in=('2-0-0', '2-0-1'), seller_id=self.seller1.id)
        )
        result = handler.get_actual_price()
        self.assertEqual(
            result,
            {
                self.seller_products['2-0-0-1'].id: Decimal('100.05'),
                self.seller_products['2-0-1-1'].id: Decimal('100.55'),
            },
        )

    def test_seller_products__products_value__get_discount(self):
        handler = self.handler(
            products=SellerProduct.objects.filter(product__name__in=('3-1-0', '2-1-1'), seller_id=self.seller0.id)
        )
        result = handler.get_discount()
        self.assertEqual(
            result,
            [
                {self.seller_products['2-1-1-0']: self.discounts[DISCOUNT_TYPES.products_value]},
                {self.seller_products['3-1-0-0']: self.discounts[DISCOUNT_TYPES.products_value]},
            ],
        )

    def test_seller_products__products_value__get_actual_price(self):
        handler = self.handler(
            products=SellerProduct.objects.filter(product__name__in=('3-1-0', '2-1-1'), seller_id=self.seller0.id)
        )
        result = handler.get_actual_price()
        self.assertEqual(
            result,
            {
                self.seller_products['2-1-1-0'].id: Decimal('161.00'),
                self.seller_products['3-1-0-0'].id: Decimal('260.00'),
            },
        )

    def test_seller_products__products_fix_price__get_discount(self):
        handler = self.handler(
            products=SellerProduct.objects.filter(product__name__in=('3-0-0', '3-1-1'), seller_id=self.seller0.id)
        )
        result = handler.get_discount()
        self.assertEqual(
            result,
            [
                {self.seller_products['3-0-0-0']: self.discounts[DISCOUNT_TYPES.products_fix_price]},
                {self.seller_products['3-1-1-0']: self.discounts[DISCOUNT_TYPES.products_fix_price]},
            ],
        )

    def test_seller_products__products_fix_price__get_actual_price(self):
        handler = self.handler(
            products=SellerProduct.objects.filter(product__name__in=('3-0-0', '3-1-1'), seller_id=self.seller1.id)
        )
        result = handler.get_actual_price()
        self.assertEqual(
            result,
            {
                self.seller_products['3-0-0-1'].id: Decimal('100.00'),
                self.seller_products['3-1-1-1'].id: Decimal('100.00'),
            },
        )

    def test_seller_products__category_percent__get_discount(self):
        handler = self.handler(
            products=SellerProduct.objects.filter(product__name__in=('4-0-0', '4-0-1'), seller_id=self.seller1.id)
        )
        result = handler.get_discount()
        self.assertEqual(
            result,
            [
                {self.seller_products['4-0-0-1']: self.discounts[DISCOUNT_TYPES.category_percent]},
                {self.seller_products['4-0-1-1']: self.discounts[DISCOUNT_TYPES.category_percent]},
            ],
        )

    def test_seller_products__category_percent__get_actual_price(self):
        handler = self.handler(
            products=SellerProduct.objects.filter(product__name__in=('4-0-0', '4-0-1'), seller_id=self.seller0.id)
        )
        result = handler.get_actual_price()
        self.assertEqual(
            result,
            {
                self.seller_products['4-0-0-0'].id: Decimal('160.00'),
                self.seller_products['4-0-1-0'].id: Decimal('160.40'),
            },
        )

    def test_seller_products__category_value__get_discount(self):
        handler = self.handler(
            products=SellerProduct.objects.filter(product__name__in=('4-1-0', '4-1-1'), seller_id=self.seller1.id)
        )
        result = handler.get_discount()
        self.assertEqual(
            result,
            [
                {self.seller_products['4-1-0-1']: self.discounts[DISCOUNT_TYPES.category_value]},
                {self.seller_products['4-1-1-1']: self.discounts[DISCOUNT_TYPES.category_value]},
            ],
        )

    def test_seller_products__category_value__get_actual_price(self):
        handler = self.handler(
            products=SellerProduct.objects.filter(product__name__in=('4-1-0', '4-1-1'), seller_id=self.seller0.id)
        )
        result = handler.get_actual_price()
        self.assertEqual(
            result,
            {
                self.seller_products['4-1-0-0'].id: Decimal('200.00'),
                self.seller_products['4-1-1-0'].id: Decimal('201.00'),
            },
        )

    def test_seller_products__category_fix_price__get_discount(self):
        handler = self.handler(
            products=SellerProduct.objects.filter(product__name__in=('5-1-0', '5-1-1'), seller_id=self.seller1.id)
        )
        result = handler.get_discount()
        self.assertEqual(
            result,
            [
                {self.seller_products['5-1-0-1']: self.discounts[DISCOUNT_TYPES.category_fix_price]},
                {self.seller_products['5-1-1-1']: self.discounts[DISCOUNT_TYPES.category_fix_price]},
            ],
        )

    def test_seller_products__category_fix_price__get_actual_price(self):
        handler = self.handler(
            products=SellerProduct.objects.filter(product__name__in=('5-1-0', '5-1-1'), seller_id=self.seller0.id)
        )
        result = handler.get_actual_price()
        self.assertEqual(
            result,
            {
                self.seller_products['5-1-0-0'].id: Decimal('450.54'),
                self.seller_products['5-1-1-0'].id: Decimal('450.54'),
            },
        )

    def test_seller_products__get_discount__all(self):
        handler = self.handler(
            products=SellerProduct.objects.filter(product__name__in=('4-0-1', '4-1-0'), seller_id=self.seller1.id)
        )
        result = handler.get_discount(all_discount=True)
        self.assertEqual(
            result,
            [
                {
                    self.seller_products['4-0-1-1']: [
                        self.discounts[DISCOUNT_TYPES.category_value],
                        self.discounts[DISCOUNT_TYPES.category_percent],
                    ]
                },
                {self.seller_products['4-1-0-1']: [self.discounts[DISCOUNT_TYPES.category_value]]},
            ],
        )

    def test_seller_product__get_discount(self):
        handler = self.handler(products=self.seller_products['3-1-0-1'])
        result = handler.get_discount()
        self.assertEqual(result, {self.seller_products['3-1-0-1']: self.discounts[DISCOUNT_TYPES.products_value]})

    def test_seller_product__get_actual_price(self):
        handler = self.handler(products=self.seller_products['2-0-1-1'])
        result = handler.get_actual_price()
        self.assertEqual(
            result,
            {self.seller_products['2-0-1-1'].id: Decimal('100.55')},
        )

    def test_seller_product__get_discount__all(self):
        handler = self.handler(products=self.seller_products['4-0-1-0'])
        result = handler.get_discount(all_discount=True)
        self.assertEqual(
            result,
            {
                self.seller_products['4-0-1-0']: [
                    self.discounts[DISCOUNT_TYPES.category_value],
                    self.discounts[DISCOUNT_TYPES.category_percent],
                ]
            },
        )

    def test_products__get_discount(self):
        handler = self.handler(
            products=Product.objects.filter(name__in=('0-1-0', '2-0-1', '3-0-0', '3-1-0', '4-1-0', '5-1-0', 'товар№1'))
        )
        result = handler.get_discount()
        self.assertEqual(
            result,
            {
                self.products['0-1-0'].id: {
                    self.seller_products['0-1-0-0']: None,
                    self.seller_products['0-1-0-1']: None,
                },
                self.products['2-0-1'].id: {
                    self.seller_products['2-0-1-0']: self.discounts['products_percent'],
                    self.seller_products['2-0-1-1']: self.discounts['products_percent'],
                },
                self.products['3-0-0'].id: {
                    self.seller_products['3-0-0-0']: self.discounts['products_fix_price'],
                    self.seller_products['3-0-0-1']: self.discounts['products_fix_price'],
                },
                self.products['3-1-0'].id: {
                    self.seller_products['3-1-0-0']: self.discounts['products_value'],
                    self.seller_products['3-1-0-1']: self.discounts['products_value'],
                },
                self.products['4-1-0'].id: {
                    self.seller_products['4-1-0-0']: self.discounts['category_value'],
                    self.seller_products['4-1-0-1']: self.discounts['category_value'],
                },
                self.products['5-1-0'].id: {
                    self.seller_products['5-1-0-0']: self.discounts['category_fix_price'],
                    self.seller_products['5-1-0-1']: self.discounts['category_fix_price'],
                },
                self.products['товар№1'].id: {},
            },
        )

    def test_products__get_actual_price(self):
        handler = self.handler(
            products=Product.objects.filter(name__in=('0-1-0', '2-0-1', '3-0-0', '3-1-0', '4-1-0', '5-1-0', 'товар№1'))
        )
        result = handler.get_actual_price()
        self.assertEqual(
            result,
            {
                self.products['0-1-0'].id: Decimal('10.05'),
                self.products['2-0-1'].id: Decimal('100.52'),
                self.products['3-0-0'].id: Decimal('100.00'),
                self.products['3-1-0'].id: Decimal('260.05'),
                self.products['4-1-0'].id: Decimal('200.05'),
                self.products['5-1-0'].id: Decimal('450.54'),
                self.products['товар№1'].id: None,
            },
        )

    def test_products__get_discount__all(self):
        handler = self.handler(products=Product.objects.filter(name__in=('4-0-1', '4-1-1')))
        result = handler.get_discount(all_discount=True)
        self.assertEqual(
            result,
            {
                self.products['4-0-1'].id: {
                    self.seller_products['4-0-1-0']: [
                        self.discounts[DISCOUNT_TYPES.category_value],
                        self.discounts[DISCOUNT_TYPES.category_percent],
                    ],
                    self.seller_products['4-0-1-1']: [
                        self.discounts[DISCOUNT_TYPES.category_value],
                        self.discounts[DISCOUNT_TYPES.category_percent],
                    ],
                },
                self.products['4-1-1'].id: {
                    self.seller_products['4-1-1-0']: [
                        self.discounts[DISCOUNT_TYPES.category_value],
                    ],
                    self.seller_products['4-1-1-1']: [
                        self.discounts[DISCOUNT_TYPES.category_value],
                    ],
                },
            },
        )

    def test_product__get_discount(self):
        handler = self.handler(products=self.products['4-0-1'])
        result = handler.get_discount()
        self.assertEqual(
            result,
            {
                self.products['4-0-1'].id: {
                    self.seller_products['4-0-1-0']: self.discounts[DISCOUNT_TYPES.category_percent],
                    self.seller_products['4-0-1-1']: self.discounts[DISCOUNT_TYPES.category_percent],
                }
            },
        )

    def test_product__get_actual_price(self):
        handler = self.handler(products=self.products['4-0-1'])
        result = handler.get_actual_price()
        self.assertEqual(result, {self.products['4-0-1'].id: Decimal('160.42')})

    def test_product__get_discount__all(self):
        handler = self.handler(products=self.products['4-0-1'])
        result = handler.get_discount(all_discount=True)
        self.assertEqual(
            result,
            {
                self.products['4-0-1'].id: {
                    self.seller_products['4-0-1-0']: [
                        self.discounts[DISCOUNT_TYPES.category_value],
                        self.discounts[DISCOUNT_TYPES.category_percent],
                    ],
                    self.seller_products['4-0-1-1']: [
                        self.discounts[DISCOUNT_TYPES.category_value],
                        self.discounts[DISCOUNT_TYPES.category_percent],
                    ],
                }
            },
        )
