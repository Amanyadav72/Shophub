import hashlib
from django.core.cache import cache

PRODUCT_CACHE_TIMEOUT = 60
PRODUCT_CACHE_VERSION_KEY = "products:catalog:version"

def get_product_cache_version():
    # Safer race-condition handling using get_or_set
    return cache.get_or_set(PRODUCT_CACHE_VERSION_KEY, 1, timeout=None)

def product_cache_key(request, prefix="view"):
    request_path = request.get_full_path()
    path_hash = hashlib.sha256(request_path.encode("utf-8")).hexdigest()
    version = get_product_cache_version()
    
    # Crucial: Add the prefix to separate lists from individual items
    return f"products:{prefix}:v{version}:{path_hash}"

def get_cached_product_response(request, prefix="view"):
    return cache.get(product_cache_key(request, prefix))

def set_cached_product_response(request, data, prefix="view"):
    cache.set(
        product_cache_key(request, prefix),
        data,
        PRODUCT_CACHE_TIMEOUT,
    )

def invalidate_product_cache():
    # If key doesn't exist, set it to 1, otherwise increment it
    try:
        cache.incr(PRODUCT_CACHE_VERSION_KEY, 1)
    except ValueError:
        cache.set(PRODUCT_CACHE_VERSION_KEY, 1, timeout=None)
