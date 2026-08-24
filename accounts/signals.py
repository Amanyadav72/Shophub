from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import CustomerProfile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_customer_profile(sender, instance, created, **kwargs):
    # Ignore the signal if we are loading data from a fixture (loaddata)
    if kwargs.get('raw', False):
        return
        
    if created:
        CustomerProfile.objects.create(user=instance)