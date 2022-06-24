from django.contrib import admin

from .models import Seller, SellerProduct


@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    """Продавец"""
    list_display = ('profile', 'address', 'email')
    list_select_related = ('profile__user', )


@admin.register(SellerProduct)
class SellerProductAdmin(admin.ModelAdmin):
    """Товар продавца"""
    list_display = ('product', 'seller', 'quantity', 'price')
    search_fields = ('product__name', 'product__category__name')
    list_filter = ('product', 'seller', 'product__category', 'product__index', 'product__is_limited_edition')
    list_select_related = ('product', 'product__category')


# @admin.register(Seller)
# class SellerAdmin(admin.ModelAdmin):
#     list_display = ("name", "description")
#     list_filter = ('product', 'seller', 'product__category',
#                    'product__index', 'product__is_limited_edition')
#     list_select_related = ('product__category', 'seller__profile__user')
