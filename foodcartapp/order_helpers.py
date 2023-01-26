from restaurateur.coords import fetch_coordinates, calculate_distance
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
