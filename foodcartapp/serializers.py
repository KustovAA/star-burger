from functools import cmp_to_key

from rest_framework import serializers
from django.db import transaction

from restaurateur.coords import fetch_coordinates, calculate_distance
from .models import Order, OrderPosition, Product
from star_burger.settings import YANDEX_API_KEY


def get_closest_restaurant(order):
    order_positions = order.positions.prefetch_related('product').all()

    available_restaurants = list(set.intersection(*[
        {
            item.restaurant
            for item in order_position.product.menu_items.filter(availability=True)
        }
        for order_position in order_positions
    ]))
    customer_coords = fetch_coordinates(YANDEX_API_KEY, order.address)

    closest_restaurant, closest_distance = None, None
    for restaurant in available_restaurants:
        distance = calculate_distance(
            fetch_coordinates(YANDEX_API_KEY, restaurant.address),
            customer_coords
        )
        if closest_restaurant is None or closest_distance > distance:
            closest_restaurant, closest_distance = restaurant, distance

    closest_restaurant.distance = closest_distance

    return closest_restaurant


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
