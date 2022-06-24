from django.contrib import admin

from .models import ViewedProduct


@admin.register(ViewedProduct)
class ViewedProductAdmin(admin.ModelAdmin):
    """Список просмотренных товаров"""

    list_display = ('id', 'user', 'product', 'modified')
    search_fields = ('user__username', 'product__name')
    list_filter = ('user', 'product')
