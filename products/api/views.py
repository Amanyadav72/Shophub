from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import filters, viewsets

from products.filters import ProductFilter
from products.models import Product
from products.pagination import ShopHubPagination

from .permissions import IsOwnerOrStaffOrReadOnly
from .serializers import ProductSerializer


@extend_schema_view(
    list=extend_schema(summary="List published products"),
    retrieve=extend_schema(summary="Retrieve a product"),
    create=extend_schema(summary="Create a product for the authenticated user"),
    partial_update=extend_schema(summary="Update a product you own"),
    destroy=extend_schema(summary="Delete a product you own"),
)
class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsOwnerOrStaffOrReadOnly]
    pagination_class = ShopHubPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ["name", "description", "categories__name"]
    ordering_fields = ["price", "created_at", "updated_at"]

    def get_queryset(self):
        queryset = Product.objects.published()
        user = self.request.user
        if user.is_authenticated:
            queryset = Product.objects.all() if user.is_staff else queryset.filter(Q(owner=user) | Q(status=Product.Status.PUBLISHED, stock__gt=0))
        return queryset.select_related("owner").prefetch_related("categories").distinct()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
