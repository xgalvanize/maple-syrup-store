"""
Test factories for creating test data
"""
import factory
from factory.django import DjangoModelFactory
from django.contrib.auth import get_user_model
from shop.models import Product, Cart, CartItem, Order, OrderItem

User = get_user_model()


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
        skip_postgeneration_save = True

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    password = factory.PostGenerationMethodCall("set_password", "testpass123")


class StaffUserFactory(UserFactory):
    class Meta:
        skip_postgeneration_save = True

    is_staff = True


class ProductFactory(DjangoModelFactory):
    class Meta:
        model = Product

    name = factory.Faker("word")
    description = factory.Faker("text", max_nb_chars=200)
    price_cents = factory.Faker("random_int", min=500, max=5000)
    image_url = factory.Faker("image_url")
    is_active = True
    inventory = factory.Faker("random_int", min=0, max=100)


class CartFactory(DjangoModelFactory):
    class Meta:
        model = Cart

    owner = factory.SubFactory(UserFactory)


class CartItemFactory(DjangoModelFactory):
    class Meta:
        model = CartItem

    cart = factory.SubFactory(CartFactory)
    product = factory.SubFactory(ProductFactory)
    quantity = 1


class OrderFactory(DjangoModelFactory):
    class Meta:
        model = Order

    user = factory.SubFactory(UserFactory)
    total_cents = 2500
    shipping_cents = 799
    shipping_zone = "ONTARIO"
    shipping_address1 = factory.Faker("street_address")
    shipping_address2 = ""
    shipping_city = factory.Faker("city")
    shipping_country = "Canada"
    shipping_region = "Ontario"
    shipping_postal = "M5H 2N2"
    status = "PENDING_PAYMENT"
    payment_method = "EMT"
    payment_reference = factory.Faker("uuid4")
    payer_email = factory.Faker("email")


class OrderItemFactory(DjangoModelFactory):
    class Meta:
        model = OrderItem

    order = factory.SubFactory(OrderFactory)
    product = factory.SubFactory(ProductFactory)
    product_name = factory.LazyAttribute(lambda obj: obj.product.name)
    quantity = 1
    price_cents = factory.LazyAttribute(lambda obj: obj.product.price_cents)
