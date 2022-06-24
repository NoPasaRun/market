import json
from typing import Callable

from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import transaction
from django.db.models import Count, Q
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView

from configuration_service.models import PeriodCash
from discounts.services import DiscountHandler
from products.models import Product
from sellers.models import SellerProduct
from user_app.forms import ProfileForm, UserUpdateForm
from user_app.models import Customer, Profile
from utils.random_instances import get_random_instances

from .cart import Cart
from .forms import OrderForm
from .models import Order, OrderItem


def redirect_to(func: Callable):
    def wrapper(request):
        cart = func(request)
        previous_abs_url = request.META.get('HTTP_REFERER')
        if previous_abs_url:
            if request.is_ajax():
                return JsonResponse({"total_sum": cart.get_total_sum(), "cart": json.dumps(cart.cart)})
            return HttpResponseRedirect(previous_abs_url)
        return cart.serialize_data()

    return wrapper


class MainView(TemplateView):
    """
    Главная страница
    """

    template_name = 'cart/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        top_goods = cache.get('top_goods')
        if top_goods:
            popular_products, popular_products_average_prices = top_goods
        else:
            popular_products = (
                Product.objects
                    .annotate(
                    order_count=Count('sellerproducts__orderitems'),
                )
                    .order_by('-index', '-order_count')[:8]
            )
            cache_settings = PeriodCash.objects.first()
            popular_products_average_prices = DiscountHandler(products=popular_products).get_actual_price()
            cache.set('top_goods', (popular_products, popular_products_average_prices), cache_settings.top_goods)
        context.update(
            {
                'popular_products': popular_products,
                'popular_products_average_prices': popular_products_average_prices,
                'products': SellerProduct.objects.select_related(
                    'product', 'seller', 'product__category', 'product__category__parent_id'
                ).filter(quantity__gt=0),
            },
        )
        return context


def change_cart(request):
    if request.method == "GET":
        seller_id = request.GET["seller_id"]
        product_id = request.GET["product_id"]
        seller_product = SellerProduct.objects.filter(seller__id=seller_id, product__id=product_id)
        if seller_product:
            seller_product: SellerProduct = seller_product[0]
            with transaction.atomic():
                delete_from_cart(request)
                get_data = request.GET.copy()
                get_data["seller_product_id"] = str(seller_product.id)
                request.GET = get_data
                add_to_cart(request)
        return HttpResponseRedirect("/cart/")


@redirect_to
def add_to_cart(request):
    if request.method == "GET":
        seller_product_id = request.GET.get("seller_product_id")
        product_id = request.GET.get("product_id")
        if not seller_product_id and product_id:
            # если получен Product вместо SellerProduct - определяем случайный SellerProduct
            q = Q(product_id=product_id)
            seller_product_qs = get_random_instances(model=SellerProduct, filter_condition=q)
            seller_product_id = seller_product_qs[0].id if len(seller_product_qs) > 0 else None
        if seller_product_id:
            amount = request.GET.get("amount", False)
            cart = Cart(request.session)
            if amount:
                cart.add(seller_product_id, int(amount))
            else:
                cart.add(seller_product_id)
            return cart


def delete_from_cart(request):
    if request.method == "GET":
        seller_product_id = request.GET["seller_product_id"]
        cart = Cart(request.session)
        cart.__delitem__(seller_product_id)
        return HttpResponseRedirect("/cart/")


@redirect_to
def remove_from_cart(request):
    if request.method == "GET":
        seller_product_id = request.GET["seller_product_id"]
        cart = Cart(request.session)
        amount = request.GET.get("amount", False)
        if amount:
            cart.remove(seller_product_id, int(amount))
        else:
            cart.remove(seller_product_id)
        return cart


class CartView(View):
    def get(self, request):
        cart = Cart(request.session)
        cart_data = cart.serialize_data()
        return render(request, "cart/cart.html", {"cart": cart_data, "total_price": cart.get_total_sum()})


def no_cart_main_page(function):
    def wrapper(self, request):
        cart = Cart(request.session)
        if cart.cart:
            return function(self, request)
        return HttpResponseRedirect("/")
    return wrapper


def no_cart_decorator(cls):
    def wrapper():
        for function_name in ["get", "post"]:
            method = getattr(cls, function_name)
            new_method = no_cart_main_page(method)
            setattr(cls, function_name, new_method)
        return cls
    return wrapper()


@no_cart_decorator
class OrderView(View):

    def get(self, request):
        cart = Cart(request.session)
        cart_data = cart.serialize_data()
        return render(request, "cart/order.html", {"cart": cart_data, "total_price": cart.get_total_sum(),
                                                   "payment_types": Order.payment_types_choices})

    def post(self, request):

        cart = Cart(request.session)
        request.POST = request.POST.copy()

        if request.POST.get("phone"):

            request.POST["phone"] = request.POST["phone"].replace("+7", "")
            request.POST["phone"] = "".join([sym for sym in request.POST["phone"] if sym.isdigit()])

        if not (request.user.is_authenticated and getattr(request.user, "profile", False)):

            user_form = UserUpdateForm(request.POST)
            profile_form = ProfileForm(request.POST)

            if user_form.is_valid() and profile_form.is_valid() or request.user.is_authenticated:
                user, created = User.objects.get_or_create(email=user_form.cleaned_data["email"])
                if created:
                    user.set_password(user_form.cleaned_data["password1"])
                    user.save()
                    profile = Profile.objects.create(user=user, **profile_form.cleaned_data)
                else:
                    profile = user.profile
            else:
                cart_data = cart.serialize_data()
                user_form.errors.update(profile_form.errors)
                return render(request, "cart/order.html", {"cart": cart_data,
                                                           "total_price": cart.get_total_sum(),
                                                           "errors": user_form.errors,
                                                           "payment_types": Order.payment_types_choices})
        else:
            profile = request.user.profile
        customer, created = Customer.objects.get_or_create(profile=profile)
        order_form = OrderForm(request.POST)
        if order_form.is_valid():
            with transaction.atomic():
                cart_data = cart.cart.copy()
                cart.__delete__()
                s_p_ids = list(map(int, cart_data.keys()))
                order = Order.objects.create(customer=customer, **order_form.cleaned_data)
                order_items = [OrderItem(seller_product=seller_product, order=order,
                                         amount=cart_data[str(seller_product.id)]["amount"])
<<<<<<< HEAD
                               for seller_product in seller_products]
                [order_item.save() for order_item in order_items]
            redirect_path = 'payment_self' if order.payment_type == 'cart' else 'payment_someone'
            return HttpResponseRedirect(redirect_path, kwargs={'order_id': order.id})
        return HttpResponse(order_form.errors, status=500)
=======
                               for seller_product in SellerProduct.objects.filter(id__in=s_p_ids)]
                for order_item in order_items:
                    order_item.save()
            return JsonResponse(json.dumps({"message": "Order has added", "status_code": 200}), safe=False)
        return JsonResponse(json.dumps({"message": order_form.errors, "status_code": 500}), safe=False)
>>>>>>> 96255057d9acb746ff6aeefbf31aee1a5e8b2dff
