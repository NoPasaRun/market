# Generated by Django 3.2.12 on 2022-05-16 14:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('browsing_history', '0002_alter_viewedproduct_user'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='viewedproduct',
            options={'ordering': ('-modified',), 'verbose_name': 'Просмотренный товар', 'verbose_name_plural': 'Просмотренные товары'},
        ),
    ]
