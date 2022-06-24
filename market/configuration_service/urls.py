from django.urls import path

from configuration_service.views import PeriodCashView

urlpatterns = [
    path('', PeriodCashView.as_view(), name='period')
]
