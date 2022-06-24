from django.contrib import admin

from .forms import OrderItemForm
from .models import Order, OrderItem


class OrderItemInline(admin.StackedInline):
    model = OrderItem


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['seller_product', 'amount', 'order']
        return []

    def get_form(self, request, obj=None, change=False, **kwargs):
        orig_self_form = self.form
        if not obj:
            self.form = OrderItemForm
        result = super().get_form(request, obj=obj, change=False, **kwargs)
        self.form = orig_self_form
        return result


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [
        OrderItemInline,
    ]
    list_display = ['id', 'customer']
    list_display_links = ['id', 'customer']
    search_fields = ['id',]
