from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Order, OrderItem


class OrderForm(forms.ModelForm):

    class Meta:
        model = Order
        exclude = ["customer", "seller_products"]
        fields = "__all__"


class OrderItemForm(forms.ModelForm):
    new_amount = forms.IntegerField(label=_("Кол-во"), required=True)

    def clean_new_amount(self):
        data = self.cleaned_data['new_amount']
        return data

    def save(self, commit=True):
        if self.instance.pk:
            raise NotImplementedError('Editing of existing OrderItem is not allowed!')

        self.instance.amount = self.cleaned_data['new_amount']
        return super().save(commit)

    class Meta:
        model = OrderItem
        fields = ['seller_product', 'new_amount', 'order']
