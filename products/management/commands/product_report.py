from django.core.management.base import BaseCommand

from products.models import Product


class Command(BaseCommand):
    help = "Display a summary report of ShopHub products"

    def handle(self, *args, **options):
        total = Product.objects.count()
        published = Product.objects.filter(status=Product.Status.PUBLISHED).count()
        unpublished = total - published
        out_of_stock = Product.objects.filter(stock=0).count()

        self.stdout.write(f"Total products: {total}")
        self.stdout.write(f"Published products: {published}")
        self.stdout.write(f"Unpublished products: {unpublished}")
        self.stdout.write(f"Out of stock: {out_of_stock}")

        self.stdout.write(self.style.SUCCESS("Product report completed."))