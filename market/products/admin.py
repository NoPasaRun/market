from django.contrib import admin

from .models import Product, ProductsGroup


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Товар
    """

    list_display = ('id', 'name', 'category', 'index', 'is_limited_edition')
    search_fields = ('name', 'category__name')
    list_filter = ('category', 'index', 'is_limited_edition')
    list_select_related = ('category',)


@admin.register(ProductsGroup)
class ProductsGroupAdmin(admin.ModelAdmin):
    """
    Группа товаров
    """

    list_display = ('id', 'name')
    search_fields = ('name',)
