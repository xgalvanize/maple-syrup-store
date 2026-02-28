from django.db import migrations, models


def backfill_product_names(apps, schema_editor):
    OrderItem = apps.get_model("shop", "OrderItem")
    for order_item in OrderItem.objects.select_related("product").all():
        if order_item.product and order_item.product.name:
            order_item.product_name = order_item.product.name
        elif not order_item.product_name:
            order_item.product_name = "Product removed"
        order_item.save(update_fields=["product_name"])


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0002_add_shipping_address_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="orderitem",
            name="product_name",
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.RunPython(backfill_product_names, migrations.RunPython.noop),
    ]
