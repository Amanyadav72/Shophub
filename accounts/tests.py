from django.contrib.auth import get_user_model
from django.test import TestCase

from .models import CustomerProfile


class CustomerProfileSignalTests(TestCase):
    def test_profile_is_created_for_new_user(self):
        user = get_user_model().objects.create_user(username="customer", password="secret")
        self.assertTrue(CustomerProfile.objects.filter(user=user).exists())
