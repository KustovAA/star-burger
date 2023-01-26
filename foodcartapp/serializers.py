from rest_framework import serializers
from django.db import transaction

from .models import Order, OrderPosition, Product
from .order_helpers import get_closest_restaurant


class ProductSerializer(serializers.Serializer):
    product = serializers.CharField(required=True)
    quantity = serializers.IntegerField(required=True)


class OrderSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=True, allow_null=False)
    last_name = serializers.CharField(required=True, allow_null=False)
    address = serializers.CharField(required=True, allow_null=False)
    phone_number = serializers.CharField(required=True, allow_null=False)
    products = ProductSerializer(
        allow_empty=False,
        allow_null=False,
        required=True,
        many=True
    )

    @transaction.atomic
    def create(self, validated_data):
        products = validated_data.pop('products')
        order = Order.objects.create(**validated_data)

        order.positions.bulk_create([
            OrderPosition(
                order=order,
                product_id=product['product'],
                price=Product.objects.get(pk=product['product']).price,
                quantity=int(product['quantity'])
            ) for product in products
        ])

        order.restaurant = get_closest_restaurant(order)
        order.save()

        return {
            **validated_data,
            'products': products
        }
