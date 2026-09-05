from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import filters, viewsets
from rest_framework.response import Response

from products.cache import get_cached_product_response, set_cached_product_response

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

    def list(self, request, *args, **kwargs):
        # Pass prefix="list"
        cached_data = get_cached_product_response(request, prefix="list")
        if cached_data is not None:
            return Response(cached_data)

        response = super().list(request, *args, **kwargs)
        if response.status_code == 200:
            set_cached_product_response(request, response.data, prefix="list")
        return response

    def retrieve(self, request, *args, **kwargs):
            # Pass prefix="detail"
            cached_data = get_cached_product_response(request, prefix="detail")
            if cached_data is not None:
                return Response(cached_data)
    
            response = super().retrieve(request, *args, **kwargs)
            if response.status_code == 200:
                set_cached_product_response(request, response.data, prefix="detail")
            return response

    

