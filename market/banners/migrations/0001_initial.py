# Generated by Django 3.2.12 on 2022-03-11 14:07

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Banner',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_to', models.DateField(verbose_name='активен до')),
                ('image', models.ImageField(upload_to='banners/', verbose_name='изображение')),
                ('title', models.CharField(max_length=250, verbose_name='заголовок')),
                ('description', models.TextField(max_length=1000, verbose_name='описание')),
                ('action_name', models.CharField(max_length=100, verbose_name='надпись на кнопке')),
            ],
            options={
                'verbose_name': 'баннер',
                'verbose_name_plural': 'баннеры',
                'ordering': ('-date_to',),
            },
        ),
    ]