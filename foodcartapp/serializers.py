from functools import cmp_to_key

from rest_framework import serializers
from django.db import transaction

from restaurateur.coords import fetch_coordinates, calculate_distance
from .models import Order, OrderPosition, Product
from star_burger.settings import YANDEX_API_KEY


def get_closest_restaurants(order):
    order_positions = order.positions.prefetch_related('product').all()

    restaurants = list(set.intersection(*[
        {
            item.restaurant
            for item in order_position.product.menu_items.filter(availability=True)
        }
        for order_position in order_positions
    ]))
    customer_coords = fetch_coordinates(YANDEX_API_KEY, order.address)

    def compare_restaurants(a, b):
        a_distance = calculate_distance(
            fetch_coordinates(YANDEX_API_KEY, a.address),
            customer_coords
        )
        b_distance = calculate_distance(
            fetch_coordinates(YANDEX_API_KEY, b.address),
            customer_coords
        )

        return a_distance < b_distance

    return [
        restaurant
        for restaurant in sorted(restaurants, key=cmp_to_key(compare_restaurants))
    ]


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

        order.closest_restaurants.add(*get_closest_restaurants(order))
        order.save()

        return {
            **validated_data,
            'products': products
        }
