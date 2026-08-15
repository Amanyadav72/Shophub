from rest_framework import serializers

from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ("id", "product", "product_name", "unit_price", "quantity", "subtotal")


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ("id", "number", "status", "payment_status", "subtotal", "shipping_cost", "tax", "total", "shipping_address", "items", "created_at", "updated_at")


class CheckoutSerializer(serializers.Serializer):
    address_id = serializers.IntegerField(min_value=1)
