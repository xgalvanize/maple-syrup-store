from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from shop.models import Product

User = get_user_model()


class Command(BaseCommand):
    help = "Seed demo user and maple syrup products"

    def handle(self, *args, **options):
        user, created = User.objects.get_or_create(username="demo_user")
        if created:
            user.set_password("demo1234")
            user.email = "demo@maplesyrup.co"
            user.save()
            self.stdout.write(self.style.SUCCESS("Created demo user: demo_user"))
        else:
            self.stdout.write("Demo user already exists")

        products = [
            {
                "name": "Light Maple Syrup 500ml",
                "description": "Golden, delicate flavor. Perfect for pancakes and waffles.",
                "price_cents": 2000,
                "image_url": "/images/light-maple.jpg",
                "inventory": 50,
            },
            {
                "name": "Dark Maple Syrup 500ml",
                "description": "Bold, rich flavor. Excellent for baking and cooking.",
                "price_cents": 2000,
                "image_url": "/images/dark-maple.jpg",
                "inventory": 50,
            },
        ]

        created_count = 0
        for data in products:
            product, created = Product.objects.get_or_create(
                name=data["name"],
                defaults=data,
            )
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f"Seeded {created_count} products"))
