# Generated by Django 3.2.12 on 2022-04-26 06:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0001_initial'),
        ('products', '0002_productsgroup'),
    ]

    operations = [
        migrations.CreateModel(
            name='Specification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=20, unique=True, verbose_name='Код характеристики')),
                ('title', models.CharField(max_length=200, verbose_name='Наименование характеристики, (и единица измерения)')),
                ('uom', models.CharField(blank=True, max_length=20, null=True, verbose_name='Единица измерения')),
                ('type', models.CharField(choices=[('list', 'Общая (материал, цвет)'), ('bool', 'Бинарная характеристика'), ('range', 'Характеристика из диапазона (диагональ, длинна, толщина)')], max_length=150, verbose_name='Тип характеристики')),
                ('categories', models.ManyToManyField(to='categories.SubCategory')),
            ],
            options={
                'verbose_name': 'Характеристика',
                'verbose_name_plural': 'Характеристики товара',
            },
        ),
        migrations.CreateModel(
            name='SpecificationValue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(blank=True, max_length=250, null=True, verbose_name='Значение характеристики')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='specs', to='products.product', verbose_name='Продукт')),
                ('specification', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='values', to='products.specification', verbose_name='Характеристика товара')),
            ],
            options={
                'verbose_name': 'Значение характеристики',
                'verbose_name_plural': 'Значения характеристик товаров',
            },
        ),
    ]
