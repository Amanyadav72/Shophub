from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase

from .models import Product


User = get_user_model()


class ProductModelTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="owner", password="password123")

    def product(self, **overrides):
        data = {"owner": self.owner, "name": "Camera", "description": "Compact camera", "price": Decimal("99.99"), "stock": 1}
        data.update(overrides)
        return Product(**data)

    def test_owner_is_required(self):
        product = self.product(owner=None)
        with self.assertRaises(ValidationError):
            product.full_clean()

    def test_published_product_requires_stock(self):
        product = self.product(stock=0, status=Product.Status.PUBLISHED)
        with self.assertRaises(ValidationError):
            product.full_clean()

    def test_availability_is_derived_from_stock(self):
        product = self.product(stock=0, is_available=True)
        product.save()
        self.assertFalse(product.is_available)
        product.stock = 3
        product.save()
        self.assertTrue(product.is_available)


class ProductTemplateOwnershipTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="owner", password="password123")
        self.other = User.objects.create_user(username="other", password="password123")
        self.product = Product.objects.create(owner=self.owner, name="Keyboard", description="Mechanical", price="50.00", stock=2, status=Product.Status.PUBLISHED)

    def test_my_products_is_owner_scoped(self):
        self.client.force_login(self.owner)
        response = self.client.get(reverse("my_products"))
        self.assertContains(response, "Keyboard")

    def test_other_user_cannot_edit_product(self):
        self.client.force_login(self.other)
        response = self.client.get(reverse("edit_product", args=[self.product.pk]))
        self.assertEqual(response.status_code, 404)

    def test_profile_is_created_on_demand_not_registration_signal(self):
        self.client.force_login(self.owner)
        self.assertFalse(hasattr(self.owner, "profile"))
        response = self.client.get(reverse("seller_profile"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(type(self.owner).objects.get(pk=self.owner.pk).profile)


class ProductAPITests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="owner", password="password123")
        self.other = User.objects.create_user(username="other", password="password123")
        self.published = Product.objects.create(owner=self.owner, name="Mouse", description="Wireless mouse", price="25.00", stock=4, status=Product.Status.PUBLISHED)
        self.draft = Product.objects.create(owner=self.owner, name="Draft product", description="Hidden", price="5.00", stock=2)
        self.url = "/api/v1/products/"

    def test_public_api_only_lists_published_products(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        names = [item["name"] for item in response.data["results"]]
        self.assertEqual(names, ["Mouse"])

    def test_authenticated_owner_can_create_product(self):
        self.client.force_authenticate(self.owner)
        response = self.client.post(self.url, {"name": "Monitor", "description": "4K", "price": "400.00", "stock": 1, "status": "PB"}, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Product.objects.get(name="Monitor").owner, self.owner)

    def test_non_owner_cannot_update_product(self):
        self.client.force_authenticate(self.other)
        response = self.client.patch(f"{self.url}{self.published.pk}/", {"price": "30.00"}, format="json")
        self.assertEqual(response.status_code, 403)

    def test_openapi_schema_is_available(self):
        response = self.client.get("/api/schema/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("/api/v1/products/", response.content.decode())
