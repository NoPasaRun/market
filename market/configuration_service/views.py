from django.shortcuts import HttpResponseRedirect
from django.views import View

from configuration_service.admin import PeriodCashForm
from configuration_service.models import PeriodCash


class PeriodCashView(View):

    def post(self, request):
        form = PeriodCashForm(request.POST)
        if form.is_valid():
            obj = PeriodCash.objects.first()
            if request.POST.get('action') == 'save':
                self.save(form, obj)
            elif request.POST.get('action') == 'drop_all':
                self.drop_all(form, obj)
            elif request.POST.get('action') == 'drop':
                self.drop(request, form, obj)
            obj.save()
        return HttpResponseRedirect('/admin/configuration_service/periodcash/')

    def save(self, form, obj):
        for field in form.fields:
            setattr(obj, field, form.data.get(field))

    def drop_all(self, form, obj):
        for field in form.fields:
            setattr(obj, field, 0)

    def drop(self, request, form, obj):
        for field in form.fields:
            if request.POST.getlist(field)[0] == 'on':
                setattr(obj, field, 0)
