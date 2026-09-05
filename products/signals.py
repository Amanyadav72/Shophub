from django.db.models.signals import m2m_changed, post_delete, post_save
from django.dispatch import receiver

from .cache import invalidate_product_cache
from .models import Product


@receiver(post_save, sender=Product)
def invalidate_product_cache_on_save(sender, instance, **kwargs):
    invalidate_product_cache()


@receiver(post_delete, sender=Product)
def invalidate_product_cache_on_delete(sender, instance, **kwargs):
    invalidate_product_cache()


@receiver(m2m_changed, sender=Product.categories.through)
def invalidate_product_cache_on_category_change(sender, instance, action, **kwargs):
    if action in {"post_add", "post_remove", "post_clear"}:
        invalidate_product_cache()