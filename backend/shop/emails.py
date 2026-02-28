from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def send_order_confirmation(order):
    """Send order confirmation email to customer"""
    subject = f"Order #{order.id} Confirmed - Maple Syrup Store"
    
    # Build order summary
    items_text = "\n".join([
        f"  • {item.product.name if item.product else 'Product'} x{item.quantity} - ${item.price_cents / 100:.2f}"
        for item in order.items.all()
    ])
    
    shipping_address = ", ".join(filter(None, [
        order.shipping_address1,
        order.shipping_address2,
        order.shipping_city,
        order.shipping_region,
        order.shipping_country,
        order.shipping_postal
    ]))
    
    message = f"""
Hi {order.user.username},

Thank you for your order! We've received your order and will process it shortly.

Order Details:
--------------
Order #: {order.id}
Status: {order.get_status_display()}
Payment Method: Interac e-Transfer
Payment Reference: {order.payment_reference}

Items Ordered:
{items_text}

Subtotal: ${(order.total_cents - order.shipping_cents) / 100:.2f}
Shipping: ${order.shipping_cents / 100:.2f}
Total: ${order.total_cents / 100:.2f}

Shipping Address:
{shipping_address}

What's Next?
------------
1. We'll verify your Interac e-Transfer payment
2. Once confirmed, we'll prepare your order for shipment
3. You'll receive a notification when your order ships

You can track your order status at: {settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else 'your account'}

Questions? Reply to this email or contact us at {settings.ADMIN_EMAIL}

Thank you for supporting local maple syrup!

- Maple Syrup Store Team
    """
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [order.user.email] if order.user.email else [order.payer_email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Failed to send customer email: {e}")
        return False


def send_admin_order_notification(order):
    """Send new order notification to admin"""
    subject = f"New Order #{order.id} - Maple Syrup Store"
    
    items_text = "\n".join([
        f"  • {item.product.name if item.product else 'Product'} x{item.quantity} - ${item.price_cents / 100:.2f}"
        for item in order.items.all()
    ])
    
    shipping_address = ", ".join(filter(None, [
        order.shipping_address1,
        order.shipping_address2,
        order.shipping_city,
        order.shipping_region,
        order.shipping_country,
        order.shipping_postal
    ]))
    
    message = f"""
New Order Received!

Order #: {order.id}
Customer: {order.user.username} ({order.user.email})
Status: {order.get_status_display()}

Payment Information:
--------------------
Method: Interac e-Transfer
Reference: {order.payment_reference}
Payer Email: {order.payer_email}
Amount: ${order.total_cents / 100:.2f}

Items:
{items_text}

Shipping Details:
-----------------
Zone: {order.shipping_zone}
Cost: ${order.shipping_cents / 100:.2f}
Address:
{shipping_address}

Next Steps:
-----------
1. Verify Interac e-Transfer in your email/bank
2. Mark order as PAID in admin panel
3. Prepare items for shipment
4. Update order status to SHIPPED

View in admin: http://localhost:8000/admin/shop/order/{order.id}/change/
    """
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.ADMIN_EMAIL],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Failed to send admin email: {e}")
        return False


def send_shipment_notification(order):
    """Send shipment notification to customer"""
    subject = f"Order #{order.id} Has Shipped - Maple Syrup Store"
    
    message = f"""
Hi {order.user.username},

Great news! Your order has shipped!

Order #: {order.id}
Status: {order.get_status_display()}

Your maple syrup is on its way to:
{order.shipping_address1}
{order.shipping_address2 + ', ' if order.shipping_address2 else ''}{order.shipping_city}, {order.shipping_region}
{order.shipping_country} {order.shipping_postal}

Estimated Delivery:
-------------------
Depending on your location, delivery typically takes:
• Local (P0R): 1-3 business days
• Ontario: 3-5 business days
• Canada: 5-10 business days
• International: 10-20 business days

Tracking information may be limited for standard shipping. If you have any questions about your order, please reply to this email.

Thank you for your purchase!

- Maple Syrup Store Team
    """
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [order.user.email] if order.user.email else [order.payer_email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Failed to send shipment email: {e}")
        return False
