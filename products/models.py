from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError

# Create your models here.
class TimeStampModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True
    

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name 

class ProductQuerySet(models.QuerySet):
    def published(self):
        """Return catalogue products that customers can buy."""
        return self.filter(status=Product.Status.PUBLISHED, stock__gt=0)
    def by_owner(self,user):
        """Returns products owned by a specific user."""
        return self.filter(owner=user)


class Product(TimeStampModel):
    class Status(models.TextChoices):
       DRAFT = "DR", "Draft"
       PUBLISHED = "PB", "Published"
       OUT_OF_STOCK = "OS", "Out of Stock"
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="products",
    )
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to="products/", blank=True, null=True)

    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    status = models.CharField(
        max_length=2,
        choices=Status,
        default=Status.DRAFT,
    )
    stock = models.PositiveIntegerField(default=0)

    is_available = models.BooleanField(default=False, editable=False)
    categories = models.ManyToManyField(Category, blank=True)

    def clean(self):
        errors = {}
        if not self.owner_id:
            errors["owner"] = "Every product must have an owner."

        if self.price is not None and self.price < 0:
            errors["price"] = "Price cannot be negative."

        if self.status == self.Status.PUBLISHED and self.stock == 0:
            errors["status"] = "A published product must have stock."

        if self.status == self.Status.OUT_OF_STOCK and self.stock > 0:
            errors["status"] = "Only products with zero stock can be marked out of stock."

        existing_product = Product.objects.none()
        if self.owner_id:
            existing_product = Product.objects.filter(owner_id=self.owner_id, name=self.name).exclude(pk=self.pk)
        if existing_product.exists():
            errors["name"] = "You already have a product with this name."
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        """Availability is derived from stock and cannot contradict it."""
        self.is_available = self.stock > 0
        super().save(*args, **kwargs)

    objects = ProductQuerySet.as_manager()
    
    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ["-updated_at"]
        constraints = [models.UniqueConstraint(
            fields=["owner","name"],
            name="unique_product_per_owner",
        )]
        indexes = [
            models.Index(fields=["status", "is_available"]),
            models.Index(fields=["name"]),
        ]
    
    def __str__(self):
        return self.name


class SellerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"
