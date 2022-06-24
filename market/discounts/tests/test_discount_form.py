# pylint: skip-file
import datetime

from django.contrib.auth.models import User
from django.test import TransactionTestCase
from django.utils import timezone

from categories.models import Category, SubCategory
from discounts.consts import DISCOUNT_TYPES
from discounts.forms import DiscountForm
from products.models import Product, ProductsGroup
from sellers.models import Seller, SellerProduct
from user_app.models import Profile


class DiscountFormTestCase(TransactionTestCase):
    form = DiscountForm

    def setUp(self):
        user = User.objects.create(username='user1')
        profile = Profile.objects.create(user=user)
        seller = Seller.objects.create(
            profile=profile, description='description', address='address', email='mail@mail.ru'
        )
        self.category = Category.objects.create(name='категория', sort_index=0)
        self.subcategory = SubCategory.objects.create(name='подкатегория', parent_id=self.category, sort_index=0)
        self.product = Product.objects.create(name='товар', category=self.subcategory)
        self.seller_product = SellerProduct.objects.create(
            product=self.product,
            seller=seller,
            quantity=100,
            price=1000,
        )
        self.product_group = ProductsGroup.objects.create(name='группа товаров')
        date = timezone.localtime(timezone.now(), timezone.get_default_timezone()).date()
        week = datetime.timedelta(days=7)
        self.initial_data = {
            'name': 'скидка',
            'date_from': date - week,
            'date_to': date + week,
            'value': 50,
            'weight': 1,
        }

    def test_product_discount__invalid(self):
        form1 = self.form(data=self.initial_data)
        data2 = {'type': DISCOUNT_TYPES.products_fix_price, 'max_products_count': 5, 'min_products_count': 1}
        data2.update(self.initial_data)
        form2 = self.form(data=data2)
        data3 = {'type': DISCOUNT_TYPES.products_percent, 'categories': [self.category]}
        data3.update(self.initial_data)
        form3 = self.form(data=data3)
        data4 = {'type': DISCOUNT_TYPES.products_value, 'product_groups': [self.product_group]}
        data4.update(self.initial_data)
        form4 = self.form(data=data4)
        data5 = {'type': DISCOUNT_TYPES.products_fix_price, 'sub_categories': [self.subcategory]}
        data5.update(self.initial_data)
        form5 = self.form(data=data5)
        self.assertFalse(form1.is_valid())
        self.assertFalse(form2.is_valid())
        self.assertFalse(form3.is_valid())
        self.assertFalse(form4.is_valid())
        self.assertFalse(form5.is_valid())

    def test_product_discount__valid(self):
        data1 = {'type': DISCOUNT_TYPES.products_fix_price, 'products': [self.product]}
        data1.update(self.initial_data)
        form1 = self.form(data=data1)
        data2 = {'type': DISCOUNT_TYPES.products_percent, 'seller_products': [self.seller_product]}
        data2.update(self.initial_data)
        form2 = self.form(data=data2)
        data3 = {
            'type': DISCOUNT_TYPES.products_value,
            'products': [self.product],
            'seller_products': [self.seller_product],
        }
        data3.update(self.initial_data)
        form3 = self.form(data=data3)
        self.assertTrue(form1.is_valid())
        self.assertTrue(form2.is_valid())
        self.assertTrue(form3.is_valid())

    def test_category_discount__invalid(self):
        form1 = self.form(data=self.initial_data)
        data2 = {'type': DISCOUNT_TYPES.category_value, 'max_products_count': 5, 'min_products_count': 1}
        data2.update(self.initial_data)
        form2 = self.form(data=data2)
        data3 = {'type': DISCOUNT_TYPES.category_fix_price, 'products': [self.product]}
        data3.update(self.initial_data)
        form3 = self.form(data=data3)
        data4 = {'type': DISCOUNT_TYPES.category_percent, 'product_groups': [self.product_group]}
        data4.update(self.initial_data)
        form4 = self.form(data=data4)
        data5 = {'type': DISCOUNT_TYPES.category_value, 'seller_products': [self.seller_product]}
        data5.update(self.initial_data)
        form5 = self.form(data=data5)
        self.assertFalse(form1.is_valid())
        self.assertFalse(form2.is_valid())
        self.assertFalse(form3.is_valid())
        self.assertFalse(form4.is_valid())
        self.assertFalse(form5.is_valid())

    def test_category_discount__valid(self):
        data1 = {'type': DISCOUNT_TYPES.category_value, 'categories': [self.category]}
        data1.update(self.initial_data)
        form1 = self.form(data=data1)
        data2 = {'type': DISCOUNT_TYPES.category_fix_price, 'sub_categories': [self.subcategory]}
        data2.update(self.initial_data)
        form2 = self.form(data=data2)
        data3 = {
            'type': DISCOUNT_TYPES.category_percent,
            'categories': [self.category],
            'sub_categories': [self.subcategory],
        }
        data3.update(self.initial_data)
        form3 = self.form(data=data3)
        self.assertTrue(form1.is_valid())
        self.assertTrue(form2.is_valid())
        self.assertTrue(form3.is_valid())

    def test_product_group_discount__invalid(self):
        form1 = self.form(data=self.initial_data)
        data2 = {'type': DISCOUNT_TYPES.product_group_fix_price, 'max_products_count': 5, 'min_products_count': 1}
        data2.update(self.initial_data)
        form2 = self.form(data=data2)
        data3 = {'type': DISCOUNT_TYPES.product_group_percent, 'categories': [self.category]}
        data3.update(self.initial_data)
        form3 = self.form(data=data3)
        data4 = {'type': DISCOUNT_TYPES.product_group_value, 'products': [self.product]}
        data4.update(self.initial_data)
        form4 = self.form(data=data4)
        data5 = {'type': DISCOUNT_TYPES.product_group_fix_price, 'seller_products': [self.seller_product]}
        data5.update(self.initial_data)
        form5 = self.form(data=data5)
        data6 = {'type': DISCOUNT_TYPES.product_group_percent, 'sub_categories': [self.subcategory]}
        data6.update(self.initial_data)
        form6 = self.form(data=data6)
        self.assertFalse(form1.is_valid())
        self.assertFalse(form2.is_valid())
        self.assertFalse(form3.is_valid())
        self.assertFalse(form4.is_valid())
        self.assertFalse(form5.is_valid())
        self.assertFalse(form6.is_valid())

    def test_product_group_discount__valid(self):
        data1 = {'type': DISCOUNT_TYPES.product_group_value, 'product_groups': [self.product_group]}
        data1.update(self.initial_data)
        form1 = self.form(data=data1)
        data2 = {'type': DISCOUNT_TYPES.product_group_fix_price, 'product_groups': [self.product_group]}
        data2.update(self.initial_data)
        form2 = self.form(data=data2)
        data3 = {'type': DISCOUNT_TYPES.product_group_percent, 'product_groups': [self.product_group]}
        data3.update(self.initial_data)
        form3 = self.form(data=data3)
        self.assertTrue(form1.is_valid())
        self.assertTrue(form2.is_valid())
        self.assertTrue(form3.is_valid())

    def test_basket_discount__invalid(self):
        form1 = self.form(data=self.initial_data)
        data2 = {'type': DISCOUNT_TYPES.basket_percent, 'product_groups': [self.product_group]}
        data2.update(self.initial_data)
        form2 = self.form(data=data2)
        data3 = {'type': DISCOUNT_TYPES.basket_value, 'categories': [self.category]}
        data3.update(self.initial_data)
        form3 = self.form(data=data3)
        data4 = {'type': DISCOUNT_TYPES.basket_fix_price, 'products': [self.product]}
        data4.update(self.initial_data)
        form4 = self.form(data=data4)
        data5 = {'type': DISCOUNT_TYPES.basket_percent, 'seller_products': [self.seller_product]}
        data5.update(self.initial_data)
        form5 = self.form(data=data5)
        data6 = {'type': DISCOUNT_TYPES.basket_value, 'sub_categories': [self.subcategory]}
        data6.update(self.initial_data)
        form6 = self.form(data=data6)
        data7 = {'type': DISCOUNT_TYPES.basket_fix_price, 'min_products_count': 3}
        data7.update(self.initial_data)
        form7 = self.form(data=data6)
        data8 = {'type': DISCOUNT_TYPES.basket_percent, 'max_products_price': 9}
        data8.update(self.initial_data)
        form8 = self.form(data=data6)
        self.assertFalse(form1.is_valid())
        self.assertFalse(form2.is_valid())
        self.assertFalse(form3.is_valid())
        self.assertFalse(form4.is_valid())
        self.assertFalse(form5.is_valid())
        self.assertFalse(form6.is_valid())
        self.assertFalse(form7.is_valid())
        self.assertFalse(form8.is_valid())

    def test_basket_discount__valid(self):
        data1 = {'type': DISCOUNT_TYPES.basket_percent, 'min_products_count': 4, 'max_products_count': 6}
        data1.update(self.initial_data)
        form1 = self.form(data=data1)
        data2 = {'type': DISCOUNT_TYPES.basket_value, 'min_products_price': 150, 'max_products_price': 250}
        data2.update(self.initial_data)
        form2 = self.form(data=data2)
        data3 = {
            'type': DISCOUNT_TYPES.basket_fix_price,
            'min_products_count': 4,
            'max_products_count': 6,
            'min_products_price': 150,
            'max_products_price': 250,
        }
        data3.update(self.initial_data)
        form3 = self.form(data=data3)
        self.assertTrue(form1.is_valid())
        self.assertTrue(form2.is_valid())
        self.assertTrue(form3.is_valid())
