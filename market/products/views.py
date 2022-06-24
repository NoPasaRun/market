from django.views.generic import DetailView

from discounts.services import DiscountHandler
from products.models import Product
from review.models import Review


class DetailProductView(DetailView):
    queryset = Product.objects.with_average_price()
    template_name = 'products/detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        product = self.get_object()

        count_review = Review.objects.count()
        review_list = Review.objects.select_related('user__profile').filter(product=product)
        context['review_list'] = review_list
        context['review_count'] = count_review

        seller_products = product.sellerproducts.select_related('seller__profile').filter(quantity__gt=0)
        context['seller_products'] = seller_products
        context['seller_products_actual_price'] = DiscountHandler(products=seller_products).get_actual_price()
        context['average_price_with_discount'] = DiscountHandler(products=product).get_actual_price()
        return context
