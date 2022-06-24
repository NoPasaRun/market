from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from products.models import Product

from .services import ProductCompare, ProductCompareList


def clear_compare_list(request):
    """
    Очистка списка сравнения товаров
    """
    prod_list = ProductCompareList(request.session)
    prod_list.clear()
    return redirect('catalog:products_compare')


def product_compare(request):
    """
    Страница сравнения товаров
    """
    prod_list = ProductCompareList(request.session)
    compare = ProductCompare(prod_list.all_products())
    product_list = compare.get_result()

    return render(request=request,
                  template_name="products_compare/compare.html",
                  context={'product_list': product_list})


def add_to_compare(request: HttpRequest, product_id: int) -> HttpResponse:
    """
    Add product to compare list by htmx
    target => #compare-count-block
    """
    if request.htmx:
        prod_list = ProductCompareList(request.session)
        product = get_object_or_404(Product, id=product_id)
        prod_list.add(product)
        return HttpResponse(f"{prod_list.count_prods_in_compare_list()}")
    return redirect('catalog:products_compare')


def remove_from_compare(request: HttpRequest, product_id: int) -> HttpResponse:
    """
    Add product to compare list by htmx
    #compare-count-block
    """
    prod_list = ProductCompareList(request.session)
    product = get_object_or_404(Product, id=product_id)
    prod_list.remove(product)
    return redirect('catalog:products_compare')
