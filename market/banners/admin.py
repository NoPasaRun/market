from django.contrib import admin

from .models import Banner


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    """
    Баннер
    """

    list_display = ('id', 'title', 'date_to')
