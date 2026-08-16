from django.contrib.auth import get_user_model
from django.test import TestCase

from accounts.models import Address
from cart.services import add_item
from products.models import Product

from .services import checkout


class CheckoutServiceTests(TestCase):
    def test_checkout_snapshots_price_and_clears_cart(self):
        user = get_user_model().objects.create_user(username="customer", password="secret")
        address = Address.objects.create(
            user=user, recipient_name="Customer", phone="9999999999", line1="1 Main Street",
            city="Delhi", state="Delhi", postal_code="110001",
        )
        product = Product.objects.create(
            owner=user,
            name="Keyboard", description="Mechanical", price="2500.00", stock=2,
            status=Product.Status.PUBLISHED,
        )
        add_item(user, product.id, 1)

        order = checkout(user, address.id)

        self.assertEqual(str(order.items.get().unit_price), "2500.00")
        self.assertEqual(str(order.items.get().subtotal), "2500.00")
        self.assertFalse(user.cart.items.exists())
        product.refresh_from_db()
        self.assertEqual(product.stock, 1)
