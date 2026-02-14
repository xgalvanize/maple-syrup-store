from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Product",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=200)),
                ("description", models.TextField(blank=True)),
                ("price_cents", models.PositiveIntegerField()),
                ("image_url", models.URLField(blank=True)),
                ("is_active", models.BooleanField(default=True)),
                ("inventory", models.PositiveIntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name="Cart",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("owner", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="cart", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="Order",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("total_cents", models.PositiveIntegerField(default=0)),
                ("shipping_cents", models.PositiveIntegerField(default=0)),
                ("shipping_zone", models.CharField(blank=True, max_length=32)),
                ("shipping_country", models.CharField(blank=True, max_length=64)),
                ("shipping_region", models.CharField(blank=True, max_length=64)),
                ("shipping_postal", models.CharField(blank=True, max_length=32)),
                ("status", models.CharField(choices=[("PENDING_PAYMENT", "Pending Payment"), ("PAID", "Paid"), ("CANCELLED", "Cancelled")], default="PENDING_PAYMENT", max_length=32)),
                ("payment_method", models.CharField(choices=[("EMT", "Email Money Transfer")], default="EMT", max_length=16)),
                ("payment_reference", models.CharField(blank=True, max_length=120)),
                ("payer_email", models.EmailField(blank=True, max_length=254)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="orders", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="CartItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("quantity", models.PositiveIntegerField(default=1)),
                ("cart", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="items", to="shop.cart")),
                ("product", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="shop.product")),
            ],
            options={
                "unique_together": {("cart", "product")},
            },
        ),
        migrations.CreateModel(
            name="OrderItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("quantity", models.PositiveIntegerField(default=1)),
                ("price_cents", models.PositiveIntegerField()),
                ("order", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="items", to="shop.order")),
                ("product", models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to="shop.product")),
            ],
        ),
    ]
