# Generated by Django 3.2.12 on 2022-05-16 14:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0004_auto_20220515_1349'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='orderitem',
            options={'verbose_name': 'Товар заказа', 'verbose_name_plural': 'Товары заказа'},
        ),
        migrations.RenameField(
            model_name='orderitem',
            old_name='count',
            new_name='amount',
        ),
    ]
