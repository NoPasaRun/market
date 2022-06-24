# Generated by Django 3.2.12 on 2022-04-09 09:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='order',
            options={'verbose_name': 'Заказ', 'verbose_name_plural': 'Заказы'},
        ),
        migrations.AddField(
            model_name='order',
            name='address',
            field=models.TextField(blank=True, max_length=200, verbose_name='Адрес'),
        ),
        migrations.AddField(
            model_name='order',
            name='city',
            field=models.CharField(blank=True, max_length=50, verbose_name='Город'),
        ),
        migrations.AddField(
            model_name='order',
            name='deliver_type',
            field=models.CharField(choices=[('express', 'Экспресс доставка'), ('ordinary', 'Обычная доставка')], default='ordinary', max_length=50, verbose_name='Способ доставки'),
        ),
        migrations.AddField(
            model_name='order',
            name='payment_type',
            field=models.CharField(choices=[('cart', 'Онлайн картой'), ('cash', 'Налом при получении'), ('someone-else', 'Афера с чужим счетом')], default='cart', max_length=50, verbose_name='Способ оплаты'),
        ),
    ]
