from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Order

@receiver(pre_save, sender=Order)
def restock_on_cancellation(sender, instance, **kwargs):
    # Skip if this is a brand new order being created
    if not instance.id:
        return
        
    try:
        old_order = Order.objects.get(id=instance.id)
    except Order.DoesNotExist:
        return

    # Trigger restock only if the status is changing to CANCELLED
    if old_order.status != Order.Status.CANCELLED and instance.status == Order.Status.CANCELLED:
        
        # Iterate over the related OrderItem objects
        for item in instance.items.select_related('product'):
            product = item.product
            product.stock += item.quantity
            
            # Using update_fields prevents overwriting concurrent database changes
            product.save(update_fields=['stock', 'updated_at'])