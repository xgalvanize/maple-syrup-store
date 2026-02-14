import graphene
from graphene_django import DjangoObjectType
from django.contrib.auth import get_user_model
from graphql_jwt.decorators import login_required
from django.db import transaction

from .models import Product, Cart, CartItem, Order, OrderItem
from .shipping import calculate_shipping_cents, estimate_shipping

User = get_user_model()


class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ("id", "username", "email")


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "description", "price_cents", "image_url", "inventory", "is_active")


class CartItemType(DjangoObjectType):
    class Meta:
        model = CartItem
        fields = ("id", "product", "quantity")


class CartType(DjangoObjectType):
    subtotal_cents = graphene.Int()

    class Meta:
        model = Cart
        fields = ("id", "owner", "items", "updated_at")

    def resolve_subtotal_cents(self, info):
        return sum(i.product.price_cents * i.quantity for i in self.items.all())


class OrderItemType(DjangoObjectType):
    class Meta:
        model = OrderItem
        fields = ("id", "product", "quantity", "price_cents")


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = (
            "id",
            "user",
            "total_cents",
            "shipping_cents",
            "shipping_zone",
            "shipping_address1",
            "shipping_address2",
            "shipping_city",
            "shipping_country",
            "shipping_region",
            "shipping_postal",
            "status",
            "payment_method",
            "payment_reference",
            "payer_email",
            "created_at",
            "items",
        )


class ShippingEstimateType(graphene.ObjectType):
    cents = graphene.Int(required=True)
    zone = graphene.String(required=True)


class RegisterUser(graphene.Mutation):
    user = graphene.Field(UserType)

    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)
        email = graphene.String()

    def mutate(self, info, username, password, email=""):
        if User.objects.filter(username=username).exists():
            raise Exception("Username already taken")
        user = User.objects.create_user(username=username, password=password, email=email)
        return RegisterUser(user=user)


class AddToCart(graphene.Mutation):
    cart = graphene.Field(CartType)

    class Arguments:
        product_id = graphene.ID(required=True)
        quantity = graphene.Int(required=False)

    @login_required
    def mutate(self, info, product_id, quantity=1):
        user = info.context.user
        product = Product.objects.get(pk=product_id, is_active=True)
        cart, _ = Cart.objects.get_or_create(owner=user)
        item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if created:
            item.quantity = max(1, quantity)
        else:
            item.quantity += max(1, quantity)
        item.save()
        return AddToCart(cart=cart)


class UpdateCartItem(graphene.Mutation):
    cart = graphene.Field(CartType)

    class Arguments:
        item_id = graphene.ID(required=True)
        quantity = graphene.Int(required=True)

    @login_required
    def mutate(self, info, item_id, quantity):
        user = info.context.user
        cart = Cart.objects.get(owner=user)
        item = CartItem.objects.get(pk=item_id, cart=cart)
        if quantity <= 0:
            item.delete()
        else:
            item.quantity = quantity
            item.save()
        return UpdateCartItem(cart=cart)


class RemoveCartItem(graphene.Mutation):
    cart = graphene.Field(CartType)

    class Arguments:
        item_id = graphene.ID(required=True)

    @login_required
    def mutate(self, info, item_id):
        user = info.context.user
        cart = Cart.objects.get(owner=user)
        CartItem.objects.filter(pk=item_id, cart=cart).delete()
        return RemoveCartItem(cart=cart)


class Checkout(graphene.Mutation):
    order = graphene.Field(OrderType)

    class Arguments:
        payment_reference = graphene.String(required=True)
        payer_email = graphene.String(required=True)
        shipping_address1 = graphene.String(required=True)
        shipping_address2 = graphene.String(required=False)
        shipping_city = graphene.String(required=True)
        shipping_country = graphene.String(required=True)
        shipping_region = graphene.String(required=True)
        shipping_postal = graphene.String(required=True)

    @login_required
    @transaction.atomic
    def mutate(
        self,
        info,
        payment_reference,
        payer_email,
        shipping_address1,
        shipping_address2="",
        shipping_city="",
        shipping_country="",
        shipping_region="",
        shipping_postal="",
    ):
        user = info.context.user
        cart = Cart.objects.get(owner=user)
        items = list(cart.items.select_related("product"))
        if not items:
            raise Exception("Cart is empty")

        subtotal = sum(i.product.price_cents * i.quantity for i in items)
        shipping_cents, shipping_zone = estimate_shipping(shipping_country, shipping_region, shipping_postal)
        total = subtotal + shipping_cents
        order = Order.objects.create(
            user=user,
            total_cents=total,
            shipping_cents=shipping_cents,
            shipping_zone=shipping_zone,
            shipping_address1=shipping_address1,
            shipping_address2=shipping_address2 or "",
            shipping_city=shipping_city,
            shipping_country=shipping_country,
            shipping_region=shipping_region,
            shipping_postal=shipping_postal,
            status="PENDING_PAYMENT",
            payment_method="EMT",
            payment_reference=payment_reference,
            payer_email=payer_email,
        )

        for item in items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price_cents=item.product.price_cents,
            )

        cart.items.all().delete()
        return Checkout(order=order)


class Query(graphene.ObjectType):
    products = graphene.List(ProductType)
    product = graphene.Field(ProductType, id=graphene.ID(required=True))
    cart = graphene.Field(CartType)
    orders = graphene.List(OrderType)
    shipping_estimate = graphene.Field(
        ShippingEstimateType,
        country=graphene.String(required=True),
        region=graphene.String(required=True),
        postal=graphene.String(required=True),
    )

    def resolve_products(self, info):
        return Product.objects.filter(is_active=True)

    def resolve_product(self, info, id):
        return Product.objects.get(pk=id)

    @login_required
    def resolve_cart(self, info):
        user = info.context.user
        cart, _ = Cart.objects.get_or_create(owner=user)
        return cart

    @login_required
    def resolve_orders(self, info):
        user = info.context.user
        return Order.objects.filter(user=user).order_by("-created_at")

    def resolve_shipping_estimate(self, info, country, region, postal):
        cents, zone = estimate_shipping(country, region, postal)
        return ShippingEstimateType(cents=cents, zone=zone)


class Mutation(graphene.ObjectType):
    register_user = RegisterUser.Field()
    add_to_cart = AddToCart.Field()
    update_cart_item = UpdateCartItem.Field()
    remove_cart_item = RemoveCartItem.Field()
    checkout = Checkout.Field()
