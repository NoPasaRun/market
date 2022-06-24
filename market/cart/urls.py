from django.urls import path

from .views import (CartView, MainView, OrderView, add_to_cart, change_cart,
                    delete_from_cart, remove_from_cart)

urlpatterns = [
    path('cart/', CartView.as_view(), name="cart"),
    path('', MainView.as_view(), name="index"),
    path('add_to_cart/', add_to_cart, name="add_to_cart"),
    path('delete_from_cart/', delete_from_cart, name="delete_from_cart"),
    path('remove_from_cart/', remove_from_cart, name="remove_from_cart"),
    path('change_cart/', change_cart, name="change_cart"),
    path('order/', OrderView.as_view(), name="order")
]
