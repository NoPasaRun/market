# Generated by Django 3.2.12 on 2022-05-16 15:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0005_auto_20220516_1723'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='amount',
            field=models.PositiveIntegerField(default=0, editable=False, verbose_name='Кол-во товара'),
        ),
    ]
