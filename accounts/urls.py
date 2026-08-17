from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    AddressViewSet,
    CsrfCookieAPIView,
    LoginAPIView,
    LogoutAPIView,
    MeAPIView,
    PasswordChangeAPIView,
    PasswordResetAPIView,
    PasswordResetConfirmAPIView,
    ProfileAPIView,
    RegisterAPIView,
)

router = DefaultRouter()
router.register("addresses", AddressViewSet, basename="address")

urlpatterns = router.urls + [
    path("auth/csrf/", CsrfCookieAPIView.as_view(), name="api-auth-csrf"),
    path("auth/register/", RegisterAPIView.as_view(), name="api-auth-register"),
    path("auth/login/", LoginAPIView.as_view(), name="api-auth-login"),
    path("auth/logout/", LogoutAPIView.as_view(), name="api-auth-logout"),
    path("auth/me/", MeAPIView.as_view(), name="api-auth-me"),
    path("auth/password/change/", PasswordChangeAPIView.as_view(), name="api-auth-password-change"),
    path("auth/password/reset/", PasswordResetAPIView.as_view(), name="api-auth-password-reset"),
    path("auth/password/reset/confirm/", PasswordResetConfirmAPIView.as_view(), name="api-auth-password-reset-confirm"),
    path("profile/", ProfileAPIView.as_view(), name="api-profile"),
]
