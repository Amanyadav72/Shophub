from django.conf import settings
from django.db import models
from django.db.models import Q


class CustomerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="customer_profile")
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s customer profile"


class Address(models.Model):
    class AddressType(models.TextChoices):
        HOME = "HOME", "Home"
        WORK = "WORK", "Work"
        OTHER = "OTHER", "Other"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="addresses")
    label = models.CharField(max_length=50, blank=True)
    address_type = models.CharField(max_length=10, choices=AddressType, default=AddressType.HOME)
    recipient_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    line1 = models.CharField(max_length=255)
    line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default="India")
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.recipient_name} — {self.city}"

    class Meta:
        ordering = ["-is_default", "-updated_at"]
        constraints = [
            models.UniqueConstraint(
                fields=("user",),
                condition=Q(is_default=True),
                name="one_default_address_per_user",
            )
        ]
