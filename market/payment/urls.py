from django.urls import path

from .views import get_payment_status, payment_card, progress_payment

urlpatterns = [
    path("self/", payment_card, name="payment_self"),
    path("someone/", payment_card, name="payment_someone"),
    path("progress_payment/", progress_payment, name="progress_payment"),
    path("status/<uuid:payment_uid>/", get_payment_status, name="get_payment_status"),
]
