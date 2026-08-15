from django.urls import path

from .views import AddressDetailAPIView, AddressListCreateAPIView, ProfileAPIView

urlpatterns = [
    path("profile/", ProfileAPIView.as_view(), name="api-profile"),
    path("addresses/", AddressListCreateAPIView.as_view(), name="api-address-list"),
    path("addresses/<int:pk>/", AddressDetailAPIView.as_view(), name="api-address-detail"),
]
