from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST

from .services import PaymentProcessing


@login_required
@require_GET
def payment_card(request):
    """
    Представление оплаты заказа
    """
    form_filename = "payment_someone_form" if "someone" in request.path else "payment_self_form"
    context = {
        'payment_form': f'payment/includes/{form_filename}.html',
        'breadcrumb_title': "Оплата заказа"
    }
    return render(request, "payment/payment.html", context)


@login_required
@require_POST
def progress_payment(request):
    """
    Отправка данных на оплату
    """
    numer = request.POST.get('numero1')
    status = PaymentProcessing(card_number=numer)
    status.processing()
    payment_uid = status.payment_uid
    return render(request, "payment/partials/progressPayment.html", {"payment_uid": payment_uid})


@login_required
@require_GET
def get_payment_status(request, payment_uid):
    """
    Получение статуса оплаты
    """
    status = PaymentProcessing()
    result = status.get_status(payment_uid)
    return render(request, "payment/partials/payment_status.html", {"result": result})
