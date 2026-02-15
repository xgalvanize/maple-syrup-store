import graphene
from graphene_django import DjangoObjectType
from django.contrib.auth import get_user_model
from graphql_jwt.decorators import login_required
from django.db import transaction

from .models import Product, Cart, CartItem, Order, OrderItem
from .shipping import calculate_shipping_cents, estimate_shipping

User = get_user_model()


def require_staff(info):
    user = info.context.user
    if not user.is_authenticated or not user.is_staff:
        raise Exception("Admin access required")
    return user


class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ("id", "username", "email", "is_staff")


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


class CreateProduct(graphene.Mutation):
    product = graphene.Field(ProductType)

    class Arguments:
        name = graphene.String(required=True)
        description = graphene.String(required=False)
        price_cents = graphene.Int(required=True)
        image_url = graphene.String(required=False)
        inventory = graphene.Int(required=False)
        is_active = graphene.Boolean(required=False)

    def mutate(
        self,
        info,
        name,
        price_cents,
        description="",
        image_url="",
        inventory=0,
        is_active=True,
    ):
        require_staff(info)
        product = Product.objects.create(
            name=name,
            description=description or "",
            price_cents=price_cents,
            image_url=image_url or "",
            inventory=max(0, inventory or 0),
            is_active=is_active if is_active is not None else True,
        )
        return CreateProduct(product=product)


class UpdateProduct(graphene.Mutation):
    product = graphene.Field(ProductType)

    class Arguments:
        product_id = graphene.ID(required=True)
        name = graphene.String(required=False)
        description = graphene.String(required=False)
        price_cents = graphene.Int(required=False)
        image_url = graphene.String(required=False)
        inventory = graphene.Int(required=False)
        is_active = graphene.Boolean(required=False)

    def mutate(
        self,
        info,
        product_id,
        name=None,
        description=None,
        price_cents=None,
        image_url=None,
        inventory=None,
        is_active=None,
    ):
        require_staff(info)
        product = Product.objects.get(pk=product_id)
        if name is not None:
            product.name = name
        if description is not None:
            product.description = description
        if price_cents is not None:
            product.price_cents = max(0, price_cents)
        if image_url is not None:
            product.image_url = image_url
        if inventory is not None:
            product.inventory = max(0, inventory)
        if is_active is not None:
            product.is_active = is_active
        product.save()
        return UpdateProduct(product=product)


class DeleteProduct(graphene.Mutation):
    ok = graphene.Boolean()

    class Arguments:
        product_id = graphene.ID(required=True)

    def mutate(self, info, product_id):
        require_staff(info)
        Product.objects.filter(pk=product_id).delete()
        return DeleteProduct(ok=True)


class UpdateOrderStatus(graphene.Mutation):
    order = graphene.Field(OrderType)

    class Arguments:
        order_id = graphene.ID(required=True)
        status = graphene.String(required=True)

    def mutate(self, info, order_id, status):
        require_staff(info)
        allowed_statuses = {choice[0] for choice in Order.STATUS_CHOICES}
        if status not in allowed_statuses:
            raise Exception("Invalid order status")
        order = Order.objects.get(pk=order_id)
        order.status = status
        order.save()
        return UpdateOrderStatus(order=order)


class MarkOrderPaid(graphene.Mutation):
    order = graphene.Field(OrderType)

    class Arguments:
        order_id = graphene.ID(required=True)

    def mutate(self, info, order_id):
        require_staff(info)
        order = Order.objects.get(pk=order_id)
        order.status = "PAID"
        order.save()
        return MarkOrderPaid(order=order)


class Query(graphene.ObjectType):
    me = graphene.Field(UserType)
    products = graphene.List(ProductType)
    product = graphene.Field(ProductType, id=graphene.ID(required=True))
    cart = graphene.Field(CartType)
    orders = graphene.List(OrderType)
    admin_products = graphene.List(ProductType)
    admin_orders = graphene.List(OrderType)
    shipping_estimate = graphene.Field(
        ShippingEstimateType,
        country=graphene.String(required=True),
        region=graphene.String(required=True),
        postal=graphene.String(required=True),
    )

    def resolve_me(self, info):
        user = info.context.user
        if user.is_authenticated:
            return user
        return None

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

    def resolve_admin_products(self, info):
        require_staff(info)
        return Product.objects.all().order_by("-id")

    def resolve_admin_orders(self, info):
        require_staff(info)
        return Order.objects.select_related("user").prefetch_related("items__product").order_by("-created_at")

    def resolve_shipping_estimate(self, info, country, region, postal):
        cents, zone = estimate_shipping(country, region, postal)
        return ShippingEstimateType(cents=cents, zone=zone)


class Mutation(graphene.ObjectType):
    register_user = RegisterUser.Field()
    add_to_cart = AddToCart.Field()
    update_cart_item = UpdateCartItem.Field()
    remove_cart_item = RemoveCartItem.Field()
    checkout = Checkout.Field()
    create_product = CreateProduct.Field()
    update_product = UpdateProduct.Field()
    delete_product = DeleteProduct.Field()
    update_order_status = UpdateOrderStatus.Field()
    mark_order_paid = MarkOrderPaid.Field()
