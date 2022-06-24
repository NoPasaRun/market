"""market URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('configuration/', include(('configuration_service.urls', 'configuration_service'),
                                    namespace='configuration')),
    path('catalog/', include(('products_compare.urls', 'products_compare'),
                                namespace='catalog')),
    path('', include('cart.urls')),
    path('payment/', include(('payment.urls', 'payment'),
                             namespace='payment')),
    path('products/', include(('products.urls', 'products'), namespace='products')),
    path('review/', include(('review.urls', 'review'), namespace='review')),
    path('account/', include("user_app.urls")),
    path('seller/', include(('sellers.urls', 'sellers'),
                            namespace='sellers')),
    path('history/', include(('browsing_history.urls', 'browsing_history'),
                             namespace='history')),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
                      path('__debug__/', include(debug_toolbar.urls)),
                  ] + urlpatterns

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
