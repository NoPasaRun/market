import datetime

from django import forms

from discounts.consts import (BASKET_DISCOUNTS, CATEGORY_DISCOUNTS,
                              DISCOUNT_TYPES, PRODUCT_DISCOUNTS,
                              PRODUCT_GROUP_DISCOUNTS)
from discounts.models import Discount


class DiscountForm(forms.ModelForm):
    """
    Форма для скидок
    """

    DISCOUNT_TYPE_FIELDS_SET = {
        'products',
        'product_groups',
        'seller_products',
        'sub_categories',
        'categories',
        'min_products_count',
        'max_products_count',
        'min_products_price',
        'max_products_price',
    }

    class Meta:
        model = Discount
        exclude = ('id',)
        help_texts = {
            'products': f'Заполнять для следующих типов скидок: '
            f'{DISCOUNT_TYPES[DISCOUNT_TYPES.products_fix_price]}, '
            f'{DISCOUNT_TYPES[DISCOUNT_TYPES.products_percent]}, '
            f'{DISCOUNT_TYPES[DISCOUNT_TYPES.products_value]}.',
            'product_groups': f'Заполнять для следующих типов скидок: '
            f'{DISCOUNT_TYPES[DISCOUNT_TYPES.product_group_fix_price]}, '
            f'{DISCOUNT_TYPES[DISCOUNT_TYPES.product_group_percent]}, '
            f'{DISCOUNT_TYPES[DISCOUNT_TYPES.product_group_value]}.',
            'seller_products': f'Заполнять для следующих типов скидок: '
            f'{DISCOUNT_TYPES[DISCOUNT_TYPES.products_fix_price]}, '
            f'{DISCOUNT_TYPES[DISCOUNT_TYPES.products_percent]}, '
            f'{DISCOUNT_TYPES[DISCOUNT_TYPES.products_value]}.',
            'sub_categories': f'Заполнять для следующих типов скидок: '
            f'{DISCOUNT_TYPES[DISCOUNT_TYPES.category_percent]}, '
            f'{DISCOUNT_TYPES[DISCOUNT_TYPES.category_value]}, '
            f'{DISCOUNT_TYPES[DISCOUNT_TYPES.category_fix_price]}.',
            'categories': f'Заполнять для следующих типов скидок: '
            f'{DISCOUNT_TYPES[DISCOUNT_TYPES.category_percent]}, '
            f'{DISCOUNT_TYPES[DISCOUNT_TYPES.category_value]}, '
            f'{DISCOUNT_TYPES[DISCOUNT_TYPES.category_fix_price]}.',
            'min_products_count': f'Заполнять для следующих типов скидок: '
            f'{DISCOUNT_TYPES[DISCOUNT_TYPES.basket_percent]}, '
            f'{DISCOUNT_TYPES[DISCOUNT_TYPES.basket_value]}, '
            f'{DISCOUNT_TYPES[DISCOUNT_TYPES.basket_fix_price]}.',
            'max_products_count': f'Заполнять для следующих типов скидок: '
            f'{DISCOUNT_TYPES[DISCOUNT_TYPES.basket_percent]}, '
            f'{DISCOUNT_TYPES[DISCOUNT_TYPES.basket_value]}, '
            f'{DISCOUNT_TYPES[DISCOUNT_TYPES.basket_fix_price]}.',
            'min_products_price': f'Заполнять для следующих типов скидок: '
            f'{DISCOUNT_TYPES[DISCOUNT_TYPES.basket_percent]}, '
            f'{DISCOUNT_TYPES[DISCOUNT_TYPES.basket_value]}, '
            f'{DISCOUNT_TYPES[DISCOUNT_TYPES.basket_fix_price]}.',
            'max_products_price': f'Заполнять для следующих типов скидок: '
            f'{DISCOUNT_TYPES[DISCOUNT_TYPES.basket_percent]}, '
            f'{DISCOUNT_TYPES[DISCOUNT_TYPES.basket_value]}, '
            f'{DISCOUNT_TYPES[DISCOUNT_TYPES.basket_fix_price]}.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.discount_type = None

    def clean(self):
        cleaned_data = super().clean()
        self.discount_type = cleaned_data.get('type')
        if self.discount_type in PRODUCT_DISCOUNTS:
            if not cleaned_data.get('products') and not cleaned_data.get('seller_products'):
                error_msg = 'Необходимо заполнить хотя бы одно из выделенных полей.'
                raise forms.ValidationError(
                    [
                        forms.ValidationError({'products': error_msg}),
                        forms.ValidationError({'seller_products': error_msg}),
                    ]
                )
            self.check_other_fields(fields={'seller_products', 'products'})
        elif self.discount_type in CATEGORY_DISCOUNTS:
            if not cleaned_data.get('sub_categories') and not cleaned_data.get('categories'):
                error_msg = 'Необходимо заполнить хотя бы одно из выделенных полей.'
                raise forms.ValidationError(
                    [
                        forms.ValidationError({'sub_categories': error_msg}),
                        forms.ValidationError({'categories': error_msg}),
                    ]
                )
            self.check_other_fields(fields={'categories', 'sub_categories'})
        elif self.discount_type in PRODUCT_GROUP_DISCOUNTS:
            if not cleaned_data.get('product_groups'):
                raise forms.ValidationError({'product_groups': 'Необходимо заполнить это поле.'})
            self.check_other_fields(fields={'product_groups'})
        elif self.discount_type in BASKET_DISCOUNTS:
            min_products_count = cleaned_data.get('min_products_count')
            max_products_count = cleaned_data.get('max_products_count')
            min_products_price = cleaned_data.get('min_products_price')
            max_products_price = cleaned_data.get('max_products_price')
            if (min_products_price and not max_products_price) or (max_products_price and not min_products_price):
                error_msg = 'Необходимо заполнить оба выделенных поля.'
                raise forms.ValidationError(
                    [
                        forms.ValidationError({'min_products_price': error_msg}),
                        forms.ValidationError({'max_products_price': error_msg}),
                    ]
                )
            if (min_products_count and not max_products_count) or (max_products_count and not min_products_count):
                error_msg = 'Необходимо заполнить оба выделенных поля.'
                raise forms.ValidationError(
                    [
                        forms.ValidationError({'min_products_count': error_msg}),
                        forms.ValidationError({'max_products_count': error_msg}),
                    ]
                )
            if not min_products_price and not max_products_price and not min_products_count and not max_products_count:
                error_msg = 'Необходимо заполнить хотя бы одну группу из граничных полей.'
                raise forms.ValidationError(
                    [
                        forms.ValidationError({'min_products_price': error_msg}),
                        forms.ValidationError({'max_products_price': error_msg}),
                        forms.ValidationError({'min_products_count': error_msg}),
                        forms.ValidationError({'max_products_count': error_msg}),
                    ]
                )
            self.check_other_fields(
                fields={'min_products_price', 'max_products_price', 'min_products_count', 'max_products_count'}
            )

    def clean_date_from(self):
        val = self.cleaned_data['date_from']
        if not val:
            val = datetime.date.today()
        return val

    def check_other_fields(self, fields: set):
        other_fields = self.DISCOUNT_TYPE_FIELDS_SET - fields
        for other_field in other_fields:
            if self.cleaned_data.get(other_field):
                raise forms.ValidationError(
                    {
                        other_field: f'Для скидки типа: "{DISCOUNT_TYPES[self.discount_type]}" '
                        f'заполнение этого поля недоступно'
                    }
                )
