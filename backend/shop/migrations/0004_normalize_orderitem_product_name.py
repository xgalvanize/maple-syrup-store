from django.db import migrations


def normalize_product_names(apps, schema_editor):
    OrderItem = apps.get_model("shop", "OrderItem")
    OrderItem.objects.filter(product_name="Product removed").update(product_name="Maple Syrup 1L")


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0003_orderitem_product_name"),
    ]

    operations = [
        migrations.RunPython(normalize_product_names, migrations.RunPython.noop),
    ]
