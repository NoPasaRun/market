from django.shortcuts import HttpResponse, render

from .services import HistoryViewService


def history_list(request):
    """
    Возвращает "отрендеренный" html шаблон со списком товаров
    для запроса с помощью HTMX
    """
    service = HistoryViewService(user=request.user)
    return render(
        request=request,
        template_name="browsing_history/includes/historyview.html",
        context={'products': service.history_list()}
    )


def history_clear(request):
    """
    Очистка истории просмотра товаров
    """
    service = HistoryViewService(user=request.user)
    service.history_clear()
    return HttpResponse('History Clear Success')


def add_to_history(request, pk):
    service = HistoryViewService(user=request.user)
    service.add(pk)
    return HttpResponse(f'Item with pk={pk} added to history success')


def remove_from_history(request, pk):
    service = HistoryViewService(user=request.user)
    service.remove(pk)
    return HttpResponse(f'Item with pk={pk} removed from history success')
