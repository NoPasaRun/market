from django.urls import path

from .views import (add_to_history, history_clear, history_list,
                    remove_from_history)

urlpatterns = [
    path('product_list', history_list, name="product_list"),
    path('<int:pk>/delete/', history_clear, name='history_clear'),
    path('<int:pk>/add/', add_to_history, name='history_add_item'),
    path('<int:pk>/clear/', remove_from_history, name='history_remove_item'),
]
