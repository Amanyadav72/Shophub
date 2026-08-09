from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'image', 'status', 'categories', 'owner', 'created_at']
        read_only_fields = ['owner', 'created_at']