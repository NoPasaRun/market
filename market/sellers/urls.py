from django.urls import path

from . import views

app_name = 'sellers'

urlpatterns = [
    path('<int:pk>/', views.SellerView.as_view(), name='seller'),
]
