
from django.urls import path

from .views import (add_to_compare, clear_compare_list, product_compare,
                    remove_from_compare)

urlpatterns = [
    path('compare/clean/', clear_compare_list, name="clear_compare_list"),
    path('compare/', product_compare, name="products_compare"),
    path('compare/<int:product_id>/add', add_to_compare, name="add_to_compare"),
    path('compare/<int:product_id>/remove', remove_from_compare, name="remove_from_compare"),
]
