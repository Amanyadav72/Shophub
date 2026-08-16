from rest_framework import serializers

from products.models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]
        read_only_fields = fields


class ProductSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            "id", "name", "description", "price", "image", "status",
            "categories", "stock", "created_at", "updated_at",
        ]
        read_only_fields = fields
