from django.core.exceptions import ValidationError as DjangoValidationError
from accounts.models import Address
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from .models import Order
from .serializers import CheckoutSerializer, OrderSerializer
from .services import checkout


class CheckoutAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    @extend_schema(request=CheckoutSerializer, responses=OrderSerializer, summary="Create an order from the current cart")
    def post(self, request):
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            order = checkout(request.user, serializer.validated_data["address_id"])
        except DjangoValidationError as error:
            return Response({"detail": error.message}, status=status.HTTP_400_BAD_REQUEST)
        except Address.DoesNotExist:
            return Response({"detail": "Shipping address not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class OrderListAPIView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related("items")


class OrderDetailAPIView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = (permissions.IsAuthenticated,)
    lookup_field = "number"

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related("items")
