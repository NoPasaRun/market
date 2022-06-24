# Generated by Django 3.2.12 on 2022-05-11 07:46

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('browsing_history', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='viewedproduct',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='viewed', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
    ]