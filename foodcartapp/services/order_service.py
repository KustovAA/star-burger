from django.db import transaction

from foodcartapp.models import Order, OrderAndProduct


@transaction.atomic
def create_order(first_name, last_name, address, phone_number, products):
    order = Order.objects.create(
        first_name=first_name,
        last_name=last_name,
        address=address,
        phone_number=phone_number,
    )

    OrderAndProduct.objects.bulk_create([
        OrderAndProduct(
            order=order,
            product_id=product['product'],
            quantity=int(product['quantity'])
        ) for product in products
    ])
