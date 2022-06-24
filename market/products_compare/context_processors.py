from .services import ProductCompareList


def product_compare_list(request):
    return {'product_compare_list': ProductCompareList(request.session)}
