# accounts/tasks.py
from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

User = get_user_model()

@shared_task(
    autoretry_for=(ConnectionError,),
    retry_backoff=True,
    retry_jitter=True,
    retry_kwargs={"max_retries": 3},
)
def send_password_reset_email(user_id, domain="127.0.0.1:8000"):
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    
    # In a decoupled React app, this URL points to the React frontend reset page
    reset_url = f"http://{domain}/api/v1/auth/password/reset/confirm/?uid={uid}&token={token}"

    send_mail(
        subject="ShopHub - Password Reset Request",
        message=(
            f"Hi {user.username},\n\n"
            f"You requested a password reset. Click the link below to set a new password:\n"
            f"{reset_url}\n\n"
            f"If you did not request this, please ignore this email."
        ),
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[user.email],
        fail_silently=False,
    )

@shared_task(
    autoretry_for=(ConnectionError,),
    retry_backoff=True,
    retry_jitter=True,
    retry_kwargs={"max_retries": 3},
)
def send_welcome_email(user_id):
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return

    send_mail(
        subject="Welcome to ShopHub!",
        message=(
            f"Hi {user.username},\n\n"
            "Thank you for registering at ShopHub. "
            "We are excited to have you!"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )