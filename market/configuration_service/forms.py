from django import forms

from configuration_service.models import PeriodCash


class PeriodCashForm(forms.ModelForm):
    class Meta:
        model = PeriodCash
        fields = ['category_menu', 'banners', 'seller', 'top_seller_goods', 'goods_list', 'detail_page']
