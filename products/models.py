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

    def __str__(self):
        return self.name 


class Product(TimeStampModel):
    class Status(models.TextChoices):
       DRAFT = "DR", "Draft"
       PUBLISHED = "PB", "Published"
       OUT_OF_STOCK = "OS", "Out of Stock"
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="products",
        null=True,
        blank=True,
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
    stock = models.IntegerField(default=0)
    def clean(self):
        existing_product = Product.objects.filter(
                    owner=self.owner,
                    name=self.name,
                ).exclude(pk=self.pk)
        if self.stock == 0 and self.status == self.Status.PUBLISHED:
            raise ValidationError(
                {"status": "Out of stock products cannot be published."}
            )
        
        if existing_product.exists():
            raise ValidationError({
                "name": "You already have a product with this name."
        })

    is_available = models.BooleanField(default=True)
    categories = models.ManyToManyField(Category, blank=True)
    class Meta:
        ordering = ["-created_at"]
        constraints = [models.UniqueConstraint(
            fields=["owner","name"],
            name="unique_product_per_owner",
        )]
    
    def __str__(self):
        return self.name


class SellerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    phone = models.CharField(max_length=15)
    address = models.TextField()
    bio = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"


#learning Purpose
#Thuough Model Only need when categories will have extra atribute after that django wont 
# abl to automaticaly do join table
"""class ProductCategory(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
    )

    is_primary = models.BooleanField(default=False)

    assigned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} -> {self.category.name}"""