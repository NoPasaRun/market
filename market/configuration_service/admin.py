from django.contrib import admin

from configuration_service.forms import PeriodCashForm
from configuration_service.models import PeriodCash


@admin.register(PeriodCash)
class PeriodCashAdmin(admin.ModelAdmin):
    form = PeriodCashForm

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}
        obj = PeriodCash.objects.all()[0]
        form = PeriodCashForm(instance=obj)
        extra_context['cash_form'] = form
        return super().changeform_view(
            request, object_id, form_url, extra_context=extra_context,
        )
