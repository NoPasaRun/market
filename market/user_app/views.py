from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import ListView

from browsing_history.models import ViewedProduct
from browsing_history.services import HistoryViewService

from .forms import ProfileForm, UserForm, UserUpdateForm
from .models import Profile


class AccountView(LoginRequiredMixin, View):

    def get(self, request):
        service = HistoryViewService(request.user)
        context = {
            'section': 'account',
            'products': service.history_list()[:3],
            'profile': get_object_or_404(Profile, user=request.user),
            'breadcrumb_title': _('Личный кабинет')
        }
        return render(request, "user_app/account.html", context)


class LogIn(LoginView):
    template_name = "user_app/login.html"


class LogOut(LogoutView):
    pass


class SignUp(View):

    def get(self, request):
        user_form = UserForm()
        profile_form = ProfileForm()
        return render(request, 'user_app/register.html', {"user_form": user_form, "profile_form": profile_form})

    def post(self, request):
        user_form = UserForm(request.POST)
        profile_form = ProfileForm(request.POST, request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            Profile(user=user, **profile_form.cleaned_data).save()
            auth_user = authenticate(user=user, password=user_form["password1"])
            login(request=request, user=auth_user)
            return HttpResponseRedirect("/account/profile/", status=201)
        user_form.errors.update(profile_form.errors)
        return render(request, 'user_app/register.html', {"user_form": user_form,
                                                          "profile_form": profile_form,
                                                          "errors": user_form.errors})


class UpdateProfileInfo(View, LoginRequiredMixin):

    def get(self, request):
        profile = get_object_or_404(Profile, pk=request.user.profile.id)
        template_name = "user_app/profile.html" if not request.htmx else "user_app/includes/profile_section.html"
        return render(request, template_name, {"profile": profile})

    def post(self, request):
        profile = get_object_or_404(Profile, pk=request.user.profile.id)
        user = profile.user

        email = request.POST.get("email")
        profile_form = ProfileForm(request.POST, request.FILES)
        user_update_form = UserUpdateForm(request.POST)
        is_authenticated_by_email = True

        if email and profile_form.is_valid():
            if user.email == email and (not request.POST.get("password1") or user_update_form.is_valid()):
                profile.update(**profile_form.cleaned_data)
                if user_update_form.is_valid():
                    new_password = user_update_form.cleaned_data["password1"]
                    user.set_password(new_password)
                user.save()
                return render(request, "user_app/profile.html", {"profile": profile,
                                                                 "updated": True})
            is_authenticated_by_email = False
        user_update_form.errors.update(profile_form.errors)
        return render(request, "user_app/profile.html", {"profile": profile,
                                                         "errors": user_update_form.errors,
                                                         "is_authenticated_by_email": is_authenticated_by_email})


class HistoryView(ListView):
    model = ViewedProduct
    context_object_name = 'products'
    template_name = "user_app/history_view.html"
