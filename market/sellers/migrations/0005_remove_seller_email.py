# Generated by Django 3.2.12 on 2022-04-22 17:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sellers', '0004_alter_sellerproduct_unique_together'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='seller',
            name='email',
        ),
    ]
