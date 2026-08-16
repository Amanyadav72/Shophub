from rest_framework import serializers

from products.models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]
        read_only_fields = fields


class ProductSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)
    categories = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), many=True, required=False
    )

    class Meta:
        model = Product
        fields = [
            "id", "owner", "name", "description", "price", "image", "status",
            "categories", "stock", "is_available", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "owner", "is_available", "created_at", "updated_at"]

    def validate_image(self, value):
        if value and value.size > 2 * 1024 * 1024:
            raise serializers.ValidationError("Image size cannot exceed 2 MB.")
        return value

    def validate(self, attrs):
        instance = self.instance
        stock = attrs.get("stock", instance.stock if instance else 0)
        status = attrs.get("status", instance.status if instance else Product.Status.DRAFT)
        if status == Product.Status.PUBLISHED and stock == 0:
            raise serializers.ValidationError({"status": "A published product must have stock."})
        if status == Product.Status.OUT_OF_STOCK and stock > 0:
            raise serializers.ValidationError({"status": "Only products with zero stock can be marked out of stock."})
        request = self.context.get("request")
        owner = self.instance.owner if self.instance else getattr(request, "user", None)
        name = attrs.get("name", instance.name if instance else None)
        if owner and owner.is_authenticated and name:
            duplicates = Product.objects.filter(owner=owner, name=name)
            if instance:
                duplicates = duplicates.exclude(pk=instance.pk)
            if duplicates.exists():
                raise serializers.ValidationError({"name": "You already have a product with this name."})
        return attrs
