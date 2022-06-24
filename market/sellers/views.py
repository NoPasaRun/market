from django.core.cache import cache
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView

import configuration_service.models
from discounts.services import DiscountHandler

from .models import Seller


class SellerView(DetailView):
    queryset = Seller.objects.prefetch_related("sellerproducts")
    template_name = "sellers/seller.html"
    context_object_name = "seller"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        seller_name = self.object.profile.user.username
        context["breadcrumb_title"] = _(f"Профиль продавца {seller_name}")
        top_seller_goods_cache = cache.get("top_seller_goods", {})
        cache_settings = configuration_service.models.PeriodCash.objects.all().first()
        if top_seller_goods_cache and (current_top_seller_goods_cache := top_seller_goods_cache.get(self.object.pk)):
            products, products_actual_prices = current_top_seller_goods_cache
        else:
            products_manager = self.object.sellerproducts
            products = products_manager.select_related('product__category__parent_id').all()
            products_actual_prices = DiscountHandler(products=products).get_actual_price()
            top_seller_goods_cache[self.object.id] = (products, products_actual_prices)
            cache.set("top_seller_goods", top_seller_goods_cache, cache_settings.seller)
        context["products"] = products
        context['products_actual_prices'] = products_actual_prices
        # TODO: запрос на топ10 товаров продавца (когда появится логика покупки)
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related('profile__user')
        return queryset
