# Generated by Django 4.1.3 on 2022-12-06 12:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0042_order_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='called_at',
            field=models.DateTimeField(null=True, verbose_name='Первый звонок'),
        ),
        migrations.AddField(
            model_name='order',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='Создано'),
        ),
        migrations.AddField(
            model_name='order',
            name='finished_at',
            field=models.DateTimeField(null=True, verbose_name='Завершено'),
        ),
    ]
