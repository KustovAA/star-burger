from rest_framework import serializers
from django.db import transaction

from .models import Order, OrderAndProduct


class ProductSerializer(serializers.Serializer):
    product = serializers.CharField(required=True)
    quantity = serializers.IntegerField(required=True)


class OrderSerializer(serializers.Serializer):
    firstname = serializers.CharField(required=True, allow_null=False)
    lastname = serializers.CharField(required=True, allow_null=False)
    address = serializers.CharField(required=True, allow_null=False)
    phonenumber = serializers.CharField(required=True, allow_null=False)
    products = ProductSerializer(
        allow_empty=False,
        allow_null=False,
        required=True,
        many=True
    )

    @transaction.atomic
    def create(self, validated_data):
        products = validated_data['products']
        order = Order.objects.create(
            first_name=validated_data['firstname'],
            last_name=validated_data['lastname'],
            address=validated_data['address'],
            phone_number=validated_data['phonenumber'],
        )

        OrderAndProduct.objects.bulk_create([
            OrderAndProduct(
                order=order,
                product_id=product['product'],
                quantity=int(product['quantity'])
            ) for product in products
        ])

        return validated_data
