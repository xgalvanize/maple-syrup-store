from django.contrib import admin
from .models import Product, Cart, CartItem, Order, OrderItem

# Admin site customization for simplicity
admin.site.site_header = "Maple Syrup Store Admin"
admin.site.site_title = "Maple Syrup Admin"
admin.site.index_title = "Manage Your Store"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "price_cents", "inventory", "is_active")
    search_fields = ("name",)
    list_filter = ("is_active",)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "owner", "updated_at")


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("id", "cart", "product", "quantity")


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "quantity", "display_price")
    can_delete = False
    
    def display_price(self, obj):
        return f"${obj.price_cents / 100:.2f}"
    display_price.short_description = "Price"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "display_total",
        "display_shipping",
        "status",
        "payer_email",
        "payment_reference",
        "shipping_address",
        "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("user__username", "payer_email", "payment_reference")
    readonly_fields = ("created_at",)
    inlines = [OrderItemInline]
    
    def display_total(self, obj):
        return f"${obj.total_cents / 100:.2f}"
    display_total.short_description = "Total"
    
    def display_shipping(self, obj):
        return f"${obj.shipping_cents / 100:.2f}"
    display_shipping.short_description = "Shipping"
    
    def shipping_address(self, obj):
        return f"{obj.shipping_region}, {obj.shipping_country} {obj.shipping_postal}"
    shipping_address.short_description = "Ship To"
