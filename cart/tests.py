from django.contrib.auth import get_user_model
from django.test import TestCase

from products.models import Product

from .models import CartItem
from .services import add_item


class CartServiceTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="customer", password="secret")
        self.product = Product.objects.create(
            name="Keyboard", description="Mechanical", price="2500.00", stock=5,
            status=Product.Status.PUBLISHED,
        )

    def test_adding_same_product_combines_quantities(self):
        add_item(self.user, self.product.id, 1)
        add_item(self.user, self.product.id, 2)
        item = CartItem.objects.get(cart__user=self.user, product=self.product)
        self.assertEqual(item.quantity, 3)
