from django.urls import path

from .views import CheckoutAPIView, OrderDetailAPIView, OrderListAPIView

urlpatterns = [
    path("checkout/", CheckoutAPIView.as_view(), name="api-checkout"),
    path("orders/", OrderListAPIView.as_view(), name="api-order-list"),
    path("orders/<str:number>/", OrderDetailAPIView.as_view(), name="api-order-detail"),
]
