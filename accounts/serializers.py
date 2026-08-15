from rest_framework import serializers

from .models import Address, CustomerProfile


class CustomerProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = CustomerProfile
        fields = ("username", "email", "phone", "avatar", "date_of_birth", "created_at", "updated_at")
        read_only_fields = ("created_at", "updated_at")


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ("id", "label", "address_type", "recipient_name", "phone", "line1", "line2", "city", "state", "postal_code", "country", "is_default", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")

    def validate(self, attrs):
        if attrs.get("is_default"):
            user = self.context["request"].user
            Address.objects.filter(user=user, is_default=True).exclude(pk=getattr(self.instance, "pk", None)).update(is_default=False)
        return attrs
