from django.urls import path

from products.views import DetailProductView

urlpatterns = [
    path('<int:pk>', DetailProductView.as_view(), name='detail')
]
