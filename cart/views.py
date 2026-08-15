from django.core.exceptions import ValidationError as DjangoValidationError
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CartItem
from .serializers import AddCartItemSerializer, CartSerializer, UpdateCartItemSerializer
from .services import add_item, get_cart, update_item


def serialized_cart(user):
    cart = get_cart(user)
    cart = cart.__class__.objects.prefetch_related("items__product").get(pk=cart.pk)
    return CartSerializer(cart).data


class CartAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        return Response(serialized_cart(request.user))


class CartItemAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        serializer = AddCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            add_item(request.user, **serializer.validated_data)
        except DjangoValidationError as error:
            return Response({"detail": error.message}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serialized_cart(request.user), status=status.HTTP_201_CREATED)


class CartItemDetailAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def patch(self, request, pk):
        serializer = UpdateCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            update_item(request.user, pk, serializer.validated_data["quantity"])
        except CartItem.DoesNotExist:
            return Response({"detail": "Cart item not found."}, status=status.HTTP_404_NOT_FOUND)
        except DjangoValidationError as error:
            return Response({"detail": error.message}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serialized_cart(request.user))

    def delete(self, request, pk):
        item = get_object_or_404(CartItem, pk=pk, cart__user=request.user)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
