# Generated by Django 3.2.12 on 2022-04-21 15:05

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('configuration_service', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='periodcash',
            name='top_goods',
            field=models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(0)], verbose_name='время кэширования топ-товаров на главной странице'),
            preserve_default=False,
        ),
    ]