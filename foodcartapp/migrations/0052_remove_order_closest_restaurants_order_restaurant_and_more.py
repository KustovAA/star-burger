# Generated by Django 4.1.3 on 2023-01-26 20:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0051_remove_order_closest_restaurant_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='closest_restaurants',
        ),
        migrations.AddField(
            model_name='order',
            name='restaurant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='foodcartapp.restaurant', verbose_name='Ресторан, который готовит заказ'),
        ),
        migrations.AlterField(
            model_name='order',
            name='payment_type',
            field=models.CharField(choices=[('OFFLINE', 'Наличными'), ('ONLINE', 'Электронно')], max_length=50, verbose_name='Способ оплаты'),
        ),
    ]
