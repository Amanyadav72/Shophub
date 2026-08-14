from rest_framework import serializers
from .models import Product, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class ProductSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price', 'image', 
            'status', 'categories', 'stock', 'is_available', 
            'owner', 'created_at'
        ]
        read_only_fields = ['owner', 'created_at']

    def validate(self, data):
        # Safely get the incoming data
        stock = data.get('stock', self.instance.stock if self.instance else 0)
        status = data.get('status', self.instance.status if self.instance else 'DR')
        name = data.get('name', self.instance.name if self.instance else None)
        
        # 1. Block out-of-stock published products
        if stock == 0 and status == 'PB':
            raise serializers.ValidationError(
                {"status": "Out of stock products cannot be published."}
            )

        # 2. Block duplicate names for the same owner
        request = self.context.get('request')
        owner = request.user if request else None

        if owner and name:
            existing = Product.objects.filter(owner=owner, name=name)
            if self.instance:
                existing = existing.exclude(pk=self.instance.pk)
                
            if existing.exists():
                raise serializers.ValidationError({
                    "name": "You already have a product with this name."
                })

        return data