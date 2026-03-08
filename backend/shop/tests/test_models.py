"""
Unit tests for Django models
"""
import pytest
from django.contrib.auth import get_user_model
from shop.models import Product, Cart, CartItem, Order, OrderItem
from shop.tests.factories import (
    UserFactory,
    ProductFactory,
    CartFactory,
    CartItemFactory,
    OrderFactory,
    OrderItemFactory,
)

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.unit
class TestProduct:
    def test_create_product(self):
        """Test creating a product"""
        product = ProductFactory(
            name="Light Maple Syrup",
            price_cents=1999,
            inventory=50
        )
        assert product.name == "Light Maple Syrup"
        assert product.price_cents == 1999
        assert product.inventory == 50
        assert product.is_active is True

    def test_product_str(self):
        """Test product string representation"""
        product = ProductFactory(name="Dark Maple Syrup")
        assert str(product) == "Dark Maple Syrup"

    def test_inactive_product(self):
        """Test creating an inactive product"""
        product = ProductFactory(is_active=False)
        assert product.is_active is False


@pytest.mark.django_db
@pytest.mark.unit
class TestCart:
    def test_create_cart(self):
        """Test creating a cart for a user"""
        user = UserFactory(username="testuser")
        cart = CartFactory(owner=user)
        assert cart.owner == user
        assert str(cart) == "Cart(testuser)"

    def test_cart_one_to_one_relationship(self):
        """Test that each user has only one cart"""
        user = UserFactory()
        cart1 = CartFactory(owner=user)
        
        # Creating another cart for the same user should fail
        with pytest.raises(Exception):
            CartFactory(owner=user)

    def test_cart_items_relationship(self):
        """Test cart items relationship"""
        cart = CartFactory()
        product1 = ProductFactory()
        product2 = ProductFactory()
        
        CartItemFactory(cart=cart, product=product1, quantity=2)
        CartItemFactory(cart=cart, product=product2, quantity=1)
        
        assert cart.items.count() == 2


@pytest.mark.django_db
@pytest.mark.unit
class TestCartItem:
    def test_create_cart_item(self):
        """Test creating a cart item"""
        cart = CartFactory()
        product = ProductFactory(name="Test Syrup")
        item = CartItemFactory(cart=cart, product=product, quantity=3)
        
        assert item.cart == cart
        assert item.product == product
        assert item.quantity == 3
        assert "Test Syrup" in str(item)
        assert "x3" in str(item)

    def test_cart_item_unique_together(self):
        """Test that cart and product combination is unique"""
        cart = CartFactory()
        product = ProductFactory()
        
        CartItemFactory(cart=cart, product=product)
        
        # Creating another item with same cart and product should fail
        with pytest.raises(Exception):
            CartItemFactory(cart=cart, product=product)


@pytest.mark.django_db
@pytest.mark.unit
class TestOrder:
    def test_create_order(self):
        """Test creating an order"""
        user = UserFactory()
        order = OrderFactory(
            user=user,
            total_cents=2500,
            shipping_cents=799,
            shipping_postal="P0R 1B0",
            status="PENDING_PAYMENT"
        )
        
        assert order.user == user
        assert order.total_cents == 2500
        assert order.shipping_cents == 799
        assert order.status == "PENDING_PAYMENT"
        assert order.payment_method == "EMT"

    def test_order_str(self):
        """Test order string representation"""
        order = OrderFactory()
        assert str(order) == f"Order({order.id})"

    def test_order_status_choices(self):
        """Test all valid order statuses"""
        valid_statuses = [
            "PENDING_PAYMENT",
            "PAID",
            "SHIPPED",
            "DELIVERED",
            "CANCELLED"
        ]
        
        for status in valid_statuses:
            order = OrderFactory(status=status)
            assert order.status == status

    def test_order_with_items(self):
        """Test order with order items"""
        order = OrderFactory()
        product1 = ProductFactory(price_cents=1500)
        product2 = ProductFactory(price_cents=2000)
        
        OrderItemFactory(order=order, product=product1, quantity=2)
        OrderItemFactory(order=order, product=product2, quantity=1)
        
        assert order.items.count() == 2
        
        # Verify total calculation
        items_total = sum(
            item.price_cents * item.quantity 
            for item in order.items.all()
        )
        assert items_total == (1500 * 2) + (2000 * 1)


@pytest.mark.django_db
@pytest.mark.unit
class TestOrderItem:
    def test_create_order_item(self):
        """Test creating an order item"""
        order = OrderFactory()
        product = ProductFactory(name="Premium Syrup", price_cents=2999)
        
        order_item = OrderItemFactory(
            order=order,
            product=product,
            product_name=product.name,
            quantity=2,
            price_cents=product.price_cents
        )
        
        assert order_item.order == order
        assert order_item.product == product
        assert order_item.product_name == "Premium Syrup"
        assert order_item.quantity == 2
        assert order_item.price_cents == 2999

    def test_order_item_with_deleted_product(self):
        """Test that order item preserves product name when product is deleted"""
        order = OrderFactory()
        product = ProductFactory(name="Limited Edition Syrup")
        
        order_item = OrderItemFactory(
            order=order,
            product=product,
            product_name=product.name
        )
        
        # Delete the product
        product_id = product.id
        product.delete()
        
        # Order item should still exist with product_name
        order_item.refresh_from_db()
        assert order_item.product is None
        assert order_item.product_name == "Limited Edition Syrup"

    def test_order_item_str(self):
        """Test order item string representation"""
        order = OrderFactory()
        order_item = OrderItemFactory(order=order)
        assert str(order_item) == f"OrderItem({order.id})"
