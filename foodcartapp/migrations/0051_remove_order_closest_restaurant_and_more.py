# Generated by Django 4.1.3 on 2023-01-04 23:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0050_alter_order_comment'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='closest_restaurant',
        ),
        migrations.AddField(
            model_name='order',
            name='closest_restaurants',
            field=models.ManyToManyField(blank=True, null=True, to='foodcartapp.restaurant', verbose_name='Ближайший ресторан'),
        ),
    ]
