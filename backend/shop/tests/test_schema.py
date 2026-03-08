"""
Integration tests for GraphQL schema (mutations and queries)
"""
import pytest
import json
from graphene.test import Client as GrapheneClient
from django.contrib.auth import get_user_model
from syrupstore.schema import schema
from shop.models import Product, Cart, CartItem, Order
from shop.tests.factories import (
    UserFactory,
    StaffUserFactory,
    ProductFactory,
    CartFactory,
    CartItemFactory,
    OrderFactory,
    OrderItemFactory,
)

User = get_user_model()


class MockContext:
    """Mock request context for GraphQL tests"""
    def __init__(self, user=None):
        self.user = user or User()


@pytest.mark.django_db
@pytest.mark.integration
class TestProductQueries:
    """Test product-related queries"""

    def test_query_products(self):
        """Test querying all active products"""
        ProductFactory.create_batch(3, is_active=True)
        ProductFactory(is_active=False)  # Should not appear
        
        client = GrapheneClient(schema)
        query = """
            query {
                products {
                    id
                    name
                    priceCents
                    isActive
                }
            }
        """
        
        result = client.execute(query, context_value=MockContext())
        assert result.get("errors") is None
        products = result["data"]["products"]
        assert len(products) == 3
        assert all(p["isActive"] for p in products)

    def test_query_single_product(self):
        """Test querying a single product by ID"""
        product = ProductFactory(name="Test Syrup", price_cents=1999)
        
        client = GrapheneClient(schema)
        query = f"""
            query {{
                product(id: "{product.id}") {{
                    id
                    name
                    priceCents
                }}
            }}
        """
        
        result = client.execute(query, context_value=MockContext())
        assert result.get("errors") is None
        data = result["data"]["product"]
        assert data["name"] == "Test Syrup"
        assert data["priceCents"] == 1999


@pytest.mark.django_db
@pytest.mark.integration
class TestUserMutations:
    """Test user registration and authentication"""

    def test_register_user(self):
        """Test user registration mutation"""
        client = GrapheneClient(schema)
        mutation = """
            mutation {
                registerUser(
                    username: "newuser",
                    password: "testpass123",
                    email: "newuser@example.com"
                ) {
                    user {
                        id
                        username
                        email
                    }
                }
            }
        """
        
        result = client.execute(mutation, context_value=MockContext())
        assert result.get("errors") is None
        user_data = result["data"]["registerUser"]["user"]
        assert user_data["username"] == "newuser"
        assert user_data["email"] == "newuser@example.com"
        
        # Verify user was created in database
        user = User.objects.get(username="newuser")
        assert user.email == "newuser@example.com"
        assert user.check_password("testpass123")

    def test_register_duplicate_username(self):
        """Test that registering duplicate username fails"""
        UserFactory(username="existinguser")
        
        client = GrapheneClient(schema)
        mutation = """
            mutation {
                registerUser(
                    username: "existinguser",
                    password: "testpass123"
                ) {
                    user {
                        id
                    }
                }
            }
        """
        
        result = client.execute(mutation, context_value=MockContext())
        assert result.get("errors") is not None
        assert "already taken" in str(result["errors"])


@pytest.mark.django_db
@pytest.mark.integration
class TestCartMutations:
    """Test cart-related mutations"""

    def test_add_to_cart(self):
        """Test adding a product to cart"""
        user = UserFactory()
        product = ProductFactory(inventory=10)
        
        client = GrapheneClient(schema)
        mutation = f"""
            mutation {{
                addToCart(productId: "{product.id}", quantity: 2) {{
                    cart {{
                        id
                        items {{
                            id
                            quantity
                            product {{ name }}
                        }}
                    }}
                }}
            }}
        """
        
        result = client.execute(mutation, context_value=MockContext(user=user))
        assert result.get("errors") is None
        cart_data = result["data"]["addToCart"]["cart"]
        assert len(cart_data["items"]) == 1
        assert cart_data["items"][0]["quantity"] == 2
        assert cart_data["items"][0]["product"]["name"] == product.name

    def test_update_cart_item(self):
        """Test updating cart item quantity"""
        user = UserFactory()
        cart = CartFactory(owner=user)
        product = ProductFactory()
        cart_item = CartItemFactory(cart=cart, product=product, quantity=1)
        
        client = GrapheneClient(schema)
        mutation = f"""
            mutation {{
                updateCartItem(itemId: "{cart_item.id}", quantity: 5) {{
                    cart {{
                        items {{
                            id
                            quantity
                        }}
                    }}
                }}
            }}
        """
        
        result = client.execute(mutation, context_value=MockContext(user=user))
        assert result.get("errors") is None
        items = result["data"]["updateCartItem"]["cart"]["items"]
        assert items[0]["quantity"] == 5

    def test_remove_cart_item(self):
        """Test removing an item from cart"""
        user = UserFactory()
        cart = CartFactory(owner=user)
        product = ProductFactory()
        cart_item = CartItemFactory(cart=cart, product=product)
        
        client = GrapheneClient(schema)
        mutation = f"""
            mutation {{
                removeCartItem(itemId: "{cart_item.id}") {{
                    cart {{
                        items {{ id }}
                    }}
                }}
            }}
        """
        
        result = client.execute(mutation, context_value=MockContext(user=user))
        assert result.get("errors") is None
        items = result["data"]["removeCartItem"]["cart"]["items"]
        assert len(items) == 0


@pytest.mark.django_db
@pytest.mark.integration
class TestCheckoutMutation:
    """Test checkout process"""

    def test_checkout_success(self):
        """Test successful checkout"""
        user = UserFactory()
        cart = CartFactory(owner=user)
        product = ProductFactory(price_cents=1500, inventory=10)
        CartItemFactory(cart=cart, product=product, quantity=2)
        
        client = GrapheneClient(schema)
        mutation = f"""
            mutation {{
                checkout(
                    paymentReference: "EMT-12345",
                    payerEmail: "payer@example.com",
                    shippingAddress1: "123 Main St",
                    shippingCity: "Toronto",
                    shippingCountry: "Canada",
                    shippingRegion: "Ontario",
                    shippingPostal: "M5H 2N2"
                ) {{
                    order {{
                        id
                        totalCents
                        shippingCents
                        status
                        items {{
                            quantity
                            priceCents
                            productName
                        }}
                    }}
                }}
            }}
        """
        
        result = client.execute(mutation, context_value=MockContext(user=user))
        assert result.get("errors") is None
        order_data = result["data"]["checkout"]["order"]
        
        # Verify order details
        assert order_data["status"] == "PENDING_PAYMENT"
        assert order_data["shippingCents"] == 799  # Ontario shipping
        assert len(order_data["items"]) == 1
        assert order_data["items"][0]["quantity"] == 2
        assert order_data["items"][0]["priceCents"] == 1500
        assert order_data["items"][0]["productName"] == product.name
        
        # Verify cart is empty
        cart.refresh_from_db()
        assert cart.items.count() == 0
        
        # Verify inventory was decremented
        product.refresh_from_db()
        assert product.inventory == 8

    def test_checkout_insufficient_inventory(self):
        """Test checkout fails with insufficient inventory"""
        user = UserFactory()
        cart = CartFactory(owner=user)
        product = ProductFactory(inventory=1)
        CartItemFactory(cart=cart, product=product, quantity=5)
        
        client = GrapheneClient(schema)
        mutation = f"""
            mutation {{
                checkout(
                    paymentReference: "EMT-12345",
                    payerEmail: "payer@example.com",
                    shippingAddress1: "123 Main St",
                    shippingCity: "Toronto",
                    shippingCountry: "Canada",
                    shippingRegion: "Ontario",
                    shippingPostal: "M5H 2N2"
                ) {{
                    order {{ id }}
                }}
            }}
        """
        
        result = client.execute(mutation, context_value=MockContext(user=user))
        assert result.get("errors") is not None
        assert "Insufficient inventory" in str(result["errors"])

    def test_checkout_empty_cart(self):
        """Test checkout fails with empty cart"""
        user = UserFactory()
        CartFactory(owner=user)  # Empty cart
        
        client = GrapheneClient(schema)
        mutation = """
            mutation {
                checkout(
                    paymentReference: "EMT-12345",
                    payerEmail: "payer@example.com",
                    shippingAddress1: "123 Main St",
                    shippingCity: "Toronto",
                    shippingCountry: "Canada",
                    shippingRegion: "Ontario",
                    shippingPostal: "M5H 2N2"
                ) {
                    order { id }
                }
            }
        """
        
        result = client.execute(mutation, context_value=MockContext(user=user))
        assert result.get("errors") is not None
        assert "Cart is empty" in str(result["errors"])


@pytest.mark.django_db
@pytest.mark.integration
class TestAdminMutations:
    """Test admin-only mutations"""

    def test_create_product_as_staff(self):
        """Test staff user can create products"""
        staff_user = StaffUserFactory()
        
        client = GrapheneClient(schema)
        mutation = """
            mutation {
                createProduct(
                    name: "New Syrup",
                    description: "Delicious",
                    priceCents: 2499,
                    inventory: 50
                ) {
                    product {
                        id
                        name
                        priceCents
                        inventory
                    }
                }
            }
        """
        
        result = client.execute(mutation, context_value=MockContext(user=staff_user))
        assert result.get("errors") is None
        product_data = result["data"]["createProduct"]["product"]
        assert product_data["name"] == "New Syrup"
        assert product_data["priceCents"] == 2499
        assert product_data["inventory"] == 50

    def test_create_product_as_non_staff_fails(self):
        """Test non-staff user cannot create products"""
        regular_user = UserFactory()
        
        client = GrapheneClient(schema)
        mutation = """
            mutation {
                createProduct(
                    name: "New Syrup",
                    priceCents: 2499
                ) {
                    product { id }
                }
            }
        """
        
        result = client.execute(mutation, context_value=MockContext(user=regular_user))
        assert result.get("errors") is not None
        assert "Admin access required" in str(result["errors"])

    def test_update_order_status(self):
        """Test staff can update order status"""
        staff_user = StaffUserFactory()
        order = OrderFactory(status="PENDING_PAYMENT")
        
        client = GrapheneClient(schema)
        mutation = f"""
            mutation {{
                updateOrderStatus(orderId: "{order.id}", status: "PAID") {{
                    order {{
                        id
                        status
                    }}
                }}
            }}
        """
        
        result = client.execute(mutation, context_value=MockContext(user=staff_user))
        assert result.get("errors") is None
        order_data = result["data"]["updateOrderStatus"]["order"]
        assert order_data["status"] == "PAID"


@pytest.mark.django_db
@pytest.mark.integration
class TestShippingEstimate:
    """Test shipping estimation query"""

    def test_shipping_estimate_ontario(self):
        """Test shipping estimate for Ontario"""
        client = GrapheneClient(schema)
        query = """
            query {
                shippingEstimate(
                    country: "Canada",
                    region: "Ontario",
                    postal: "M5H 2N2"
                ) {
                    cents
                    zone
                }
            }
        """
        
        result = client.execute(query, context_value=MockContext())
        assert result.get("errors") is None
        estimate = result["data"]["shippingEstimate"]
        assert estimate["cents"] == 799
        assert estimate["zone"] == "ONTARIO"

    def test_shipping_estimate_local_radius(self):
        """Test shipping estimate for local radius"""
        client = GrapheneClient(schema)
        query = """
            query {
                shippingEstimate(
                    country: "Canada",
                    region: "Ontario",
                    postal: "P0R 1B0"
                ) {
                    cents
                    zone
                }
            }
        """
        
        result = client.execute(query, context_value=MockContext())
        assert result.get("errors") is None
        estimate = result["data"]["shippingEstimate"]
        assert estimate["cents"] == 499
        assert estimate["zone"] == "LOCAL_RADIUS"
