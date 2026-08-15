from django.urls import path

from .views import CartAPIView, CartItemAPIView, CartItemDetailAPIView

urlpatterns = [
    path("cart/", CartAPIView.as_view(), name="api-cart"),
    path("cart/items/", CartItemAPIView.as_view(), name="api-cart-items"),
    path("cart/items/<int:pk>/", CartItemDetailAPIView.as_view(), name="api-cart-item-detail"),
]
