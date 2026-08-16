from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APITestCase

from .models import Address, CustomerProfile


class CustomerProfileSignalTests(TestCase):
    def test_profile_is_created_for_new_user(self):
        user = get_user_model().objects.create_user(username="customer", password="secret")
        self.assertTrue(CustomerProfile.objects.filter(user=user).exists())


class AccountAPITests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="customer", email="customer@example.com", password="VerySecurePass123!"
        )

    def test_register_login_and_me(self):
        response = self.client.post("/api/v1/auth/register/", {
            "username": "new-customer", "email": "new@example.com", "password": "AnotherSecurePass123!",
        }, format="json")
        self.assertEqual(response.status_code, 201)
        response = self.client.post("/api/v1/auth/login/", {
            "username": "new-customer", "password": "AnotherSecurePass123!",
        }, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["username"], "new-customer")
        response = self.client.get("/api/v1/auth/me/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["username"], "new-customer")
        response = self.client.post("/api/v1/auth/logout/", format="json")
        self.assertEqual(response.status_code, 204)
        response = self.client.get("/api/v1/auth/me/")
        self.assertEqual(response.status_code, 403)

    def test_customer_cannot_access_another_customers_address(self):
        other = get_user_model().objects.create_user(username="other", password="VerySecurePass123!")
        address = Address.objects.create(
            user=other, recipient_name="Other", phone="9999999999", line1="1 Main Street",
            city="Delhi", state="Delhi", postal_code="110001",
        )
        self.client.force_authenticate(self.user)
        response = self.client.get(f"/api/v1/addresses/{address.pk}/")
        self.assertEqual(response.status_code, 404)

    def test_new_default_address_replaces_existing_default(self):
        self.client.force_authenticate(self.user)
        first = Address.objects.create(
            user=self.user, recipient_name="Customer", phone="9999999999", line1="1 Main Street",
            city="Delhi", state="Delhi", postal_code="110001", is_default=True,
        )
        response = self.client.post("/api/v1/addresses/", {
            "recipient_name": "Customer", "phone": "9999999999", "line1": "2 Main Street",
            "city": "Delhi", "state": "Delhi", "postal_code": "110001", "is_default": True,
        }, format="json")
        self.assertEqual(response.status_code, 201)
        first.refresh_from_db()
        self.assertFalse(first.is_default)
        self.assertTrue(Address.objects.get(pk=response.data["id"]).is_default)
