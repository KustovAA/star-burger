from django.db import models
from django.db.models import Sum, F
from django.utils import timezone
from django.core.validators import MinValueValidator
from phonenumber_field.modelfields import PhoneNumberField


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class OrderManager(models.Manager):
    def with_price(self):
        return self.annotate(price=Sum(F('positions__price') * F('positions__quantity')))


class Order(models.Model):
    CREATED = 'CREATED'
    COOKING = 'COOKING'
    DELIVERY = 'DELIVERY'
    DONE = 'DONE'
    STATUSES = [
        (CREATED, 'Создан'),
        (COOKING, 'Готовится'),
        (DELIVERY, 'У курьера'),
        (DONE, 'Готов'),
    ]

    OFFLINE = 'OFFLINE'
    ONLINE = 'ONLINE'
    PAYMENT_TYPES = [
        (OFFLINE, 'Наличными'),
        (ONLINE, 'Электронно'),
    ]

    first_name = models.CharField(max_length=500, verbose_name='Имя')
    last_name = models.CharField(max_length=500, verbose_name='Фамилия')
    address = models.CharField(max_length=1000, verbose_name='Адрес')
    phone_number = PhoneNumberField(verbose_name='Номер телефона')
    status = models.CharField(
        max_length=50,
        default=CREATED,
        choices=STATUSES,
        verbose_name='Статус заказа',
        db_index=True
    )
    comment = models.TextField(verbose_name='Комментарий', blank=True)
    created_at = models.DateTimeField(verbose_name='Создано', default=timezone.now)
    called_at = models.DateTimeField(verbose_name='Первый звонок', null=True, blank=True)
    finished_at = models.DateTimeField(verbose_name='Завершено', null=True, blank=True)
    payment_type = models.CharField(
        max_length=50,
        choices=PAYMENT_TYPES,
        verbose_name='Способ оплаты'
    )
    active_restaurant = models.ForeignKey(
        Restaurant,
        verbose_name='Ресторан, который готовит заказ',
        related_name='orders',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    objects = OrderManager()

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.address}"


class OrderPosition(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        verbose_name='Заказ',
        related_name='positions'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='Товар',
        related_name='positions'
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    quantity = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[MinValueValidator(1)]
    )

    def __str__(self):
        return f"{self.product.name} - {self.order}"

    class Meta:
        verbose_name = 'заказ и продукт'
        verbose_name_plural = 'заказы и продукты'
