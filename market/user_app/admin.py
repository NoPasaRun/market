from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from .models import Customer, Profile


class ProfileAdmin(admin.ModelAdmin):
    list_display_links = ["id", "user"]
    list_display = ["id", "user"]


class CustomerAdmin(admin.ModelAdmin):
    list_display_links = ['id', 'profile']
    list_display = ["id", "profile"]


class UserCreationFormWithEmail(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'] = forms.EmailField(label=_("Почта"), max_length=75)


UserAdmin.add_form = UserCreationFormWithEmail
UserAdmin.add_fieldsets = (
    (None, {
        'classes': ('wide',),
        'fields': ('email', 'password1', 'password2',)
    }),
)
UserAdmin.list_display_links = ("id", "email")
UserAdmin.list_display = ("id", "email", "is_staff")

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Profile, ProfileAdmin)
