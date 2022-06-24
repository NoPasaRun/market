# Generated by Django 3.2.12 on 2022-03-16 08:15

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('products', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='id')),
                ('review_text', models.TextField(verbose_name='текст отзыва')),
                ('added_at', models.DateTimeField(auto_now_add=True, verbose_name='добавлен')),
                ('product', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='products.product', verbose_name='товар')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='пользователь')),
            ],
        ),
    ]