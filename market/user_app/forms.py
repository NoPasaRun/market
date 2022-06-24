from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Profile


class UserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["password1", "password2", "email"]


class ProfileForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ["avatar", "name", "phone", "birth_date"]


class UserUpdateForm(forms.Form):
    password1 = forms.CharField(widget=forms.PasswordInput(), required=False)
    password2 = forms.CharField(widget=forms.PasswordInput(), required=False)
    email = forms.EmailField()

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        user = User.objects.filter(email=cleaned_data.get("email"))
        if user:
            if user[0].is_authenticated and password1 == "" == password2:
                return
        if not password1:
            raise forms.ValidationError(
                "Заполните поля для пароля!"
            )
        if password1 != password2:
            raise forms.ValidationError(
                "Пароли не совпадают!"
            )
        if len(password1) < 10:
            raise forms.ValidationError(
                "Пароль должен содержать больше 9 символов!"
            )
        if user:
            user = user[0]
            if not user.check_password(cleaned_data.get("password1")):
                raise forms.ValidationError(
                    "Неверный пароль!"
                )
