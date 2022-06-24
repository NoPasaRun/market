from cart.cart import Cart


class CartTotalPriceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_template_response(self, request, response):
        response.context_data['cart_total_price'] = Cart(request.session).get_total_sum()
        response.context_data['cart_total_price_old'] = Cart(request.session).get_total_sum(without_discount=True)
        return response
