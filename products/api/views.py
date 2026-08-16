from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import filters, viewsets

from products.filters import ProductFilter
from products.models import Product
from products.pagination import ShopHubPagination

from .serializers import ProductSerializer


@extend_schema_view(
    list=extend_schema(summary="List published products"),
    retrieve=extend_schema(summary="Retrieve a product"),
)
class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """Public customer catalogue; all product writes happen in staff templates."""
    serializer_class = ProductSerializer
    pagination_class = ShopHubPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ["name", "description", "categories__name"]
    ordering_fields = ["price", "created_at", "updated_at"]

    def get_queryset(self):
        return Product.objects.published().prefetch_related("categories").distinct()
