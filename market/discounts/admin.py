from django.contrib import admin

from .forms import DiscountForm
from .models import Discount


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    """
    Скидка
    """

    form = DiscountForm
    list_display = ('id', 'name', 'type', 'value', 'weight', 'date_from', 'date_to')
    search_fields = ('id', 'name',)
    list_filter = ('type', 'weight')
