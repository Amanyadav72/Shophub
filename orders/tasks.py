# orders/tasks.py
from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from .models import Order

@shared_task(
    autoretry_for=(ConnectionError,),
    retry_backoff=True,
    retry_jitter=True,
    retry_kwargs={"max_retries": 3},
)
def send_order_confirmation_email(order_id):
    try:
        order = Order.objects.select_related("user").get(pk=order_id)
    except Order.DoesNotExist:
        return

    send_mail(
        subject=f"ShopHub Order Confirmation: {order.number}",
        message=(
            f"Hi {order.user.username},\n\n"
            f"Your order {order.number} has been placed successfully!\n"
            f"Total: ${order.total}\n\n"
            f"Thank you for shopping with ShopHub!"
        ),
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[order.user.email],
        fail_silently=False,
    )