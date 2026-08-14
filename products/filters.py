import django_filters
from .models import Product

class ProductFilter(django_filters.FilterSet):
    # Custom URL parameters for price ranges
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr='lte')
    
    # Custom URL parameters for stock ranges
    min_stock = django_filters.NumberFilter(field_name="stock", lookup_expr='gte')
    max_stock = django_filters.NumberFilter(field_name="stock", lookup_expr='lte')

    class Meta:
        model = Product
        # We also include 'categories' here so we don't lose our exact match filter
        fields = ['categories']