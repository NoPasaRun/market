import os
from datetime import datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch.dispatcher import receiver
from django.utils.translation import gettext_lazy as _
from django_hybrid_attributes import hybrid_property
from model_utils.models import TimeStampedModel

User.__str__ = lambda self: self.email
User.REQUIRED_FIELDS.append("username")
User.REQUIRED_FIELDS.remove("email")
User._meta.get_field('email').blank = False  # pylint: disable=W0212
User._meta.get_field('email')._unique = True  # pylint: disable=W0212
User._meta.get_field('username').blank = True  # pylint: disable=W0212
User._meta.get_field('username')._unique = False  # pylint: disable=W0212
User.USERNAME_FIELD = "email"


def delete_file(file: str):
    path_to_file = str(settings.MEDIA_ROOT / file)
    if os.path.isfile(path_to_file):
        os.remove(path_to_file)


class Profile(TimeStampedModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, verbose_name=_("Пользователь"), on_delete=models.CASCADE)
    avatar = models.ImageField(verbose_name=_("Аватар"), upload_to="avatars/", blank=True, null=True)
    name_regex = RegexValidator(regex=r"^[a-zA-Z]{2,15}\s[a-zA-Z]{2,15}(?:\s[a-zA-Z]{2,15})?$|"
                                      r"^[а-яА-ЯёЁ]{2,15}\s[а-яА-ЯёЁ]{2,15}(?:\s[а-яА-ЯёЁ]{2,15})?$",
                                message="Name must be in a format LastName MiddleName[Optional] FirstName. "
                                        "Also make sure your name is written in the same language")
    name = models.CharField(validators=[name_regex], verbose_name=_("ФИO"), max_length=150, blank=True, null=True)
    phone_regex = RegexValidator(regex=r'\d{10}',
                                 message="Phone number contain ten digits")
    phone = models.CharField(validators=[phone_regex], max_length=10, blank=True,
                             null=True, verbose_name=_("Телефон"))
    birth_date = models.DateField(verbose_name=_("Дата рождения"), blank=True, null=True)

    def __str__(self):
        if self.birth_date:
            years = str(self.age)
            year_title = "год" if int(years[-1]) in range(1, 5) else "лет"
            if int(years[-1]) in range(2, 5):
                year_title += "а"
            return f"{self.user} - {years} {year_title}"
        return f"{self.user}"

    class Meta:
        verbose_name = _("Профиль")
        verbose_name_plural = _("Профили")

    def update(self, **kwargs):
        avatar_url = str(self.avatar)
        for field, value in kwargs.items():
            if value:
                setattr(self, field, value)
        self.save()
        if avatar_url != str(self.avatar):
            delete_file(avatar_url)

    @property
    def photo_url(self):
        if self.avatar and hasattr(self.avatar, 'url'):
            return self.avatar.url
        return f'{settings.MEDIA_URL}no_photo.jpg'

    @hybrid_property
    def age(self) -> int:
        timedelta = datetime.date(datetime.now()) - self.birth_date
        years = timedelta.days // 365
        return years

    @property
    def is_adult(self):
        return self.age >= 18  # pylint: disable=W0143


class Customer(models.Model):
    profile = models.OneToOneField(Profile, verbose_name=_("Профиль"), on_delete=models.CASCADE)

    def __str__(self):
        return str(self.profile)

    class Meta:
        verbose_name = _("Покупатель")
        verbose_name_plural = _("Покупатели")


@receiver(post_delete, sender=Profile)
def delete_avatar(sender, instance, *args, **kwargs):
    if instance.avatar:
        delete_file(str(instance.avatar))
