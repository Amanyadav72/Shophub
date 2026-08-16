from django.contrib.auth import authenticate, get_user_model, login, logout, update_session_auth_hash
from django.contrib.auth.tokens import default_token_generator
from django.utils.decorators import method_decorator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions, serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Address, CustomerProfile
from .serializers import (
    AddressSerializer,
    CustomerProfileSerializer,
    PasswordChangeSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    RegisterSerializer,
    UserSerializer,
)


class EmptySerializer(serializers.Serializer):
    pass


class ProfileAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = CustomerProfileSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        profile, _ = CustomerProfile.objects.get_or_create(user=self.request.user)
        return profile


class AddressListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = AddressSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save()


class AddressDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AddressSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)


class RegisterAPIView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = (permissions.AllowAny,)

    @extend_schema(summary="Register a customer account")
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


@method_decorator(ensure_csrf_cookie, name="dispatch")
class CsrfCookieAPIView(APIView):
    permission_classes = (permissions.AllowAny,)

    @extend_schema(responses={204: None}, summary="Set the CSRF cookie required for session-authenticated requests")
    def get(self, request):
        return Response(status=status.HTTP_204_NO_CONTENT)


@method_decorator(csrf_protect, name="dispatch")
class LoginAPIView(APIView):
    permission_classes = (permissions.AllowAny,)

    @extend_schema(request={"application/json": {"type": "object", "properties": {"username": {"type": "string"}, "password": {"type": "string", "format": "password"}}, "required": ["username", "password"]}}, responses=UserSerializer, summary="Log in and create a Django session")
    def post(self, request):
        username = request.data.get("username", "")
        password = request.data.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response({"detail": "Invalid username or password."}, status=status.HTTP_400_BAD_REQUEST)
        login(request, user)
        return Response(UserSerializer(user).data)


@method_decorator(csrf_protect, name="dispatch")
class LogoutAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = EmptySerializer

    @extend_schema(responses={204: None}, summary="Log out and clear the current Django session")
    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user


class PasswordChangeAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    @extend_schema(request=PasswordChangeSerializer, responses={204: None}, summary="Change the current user's password")
    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save(update_fields=["password"])
        update_session_auth_hash(request, request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class PasswordResetAPIView(APIView):
    permission_classes = (permissions.AllowAny,)

    @extend_schema(request=PasswordResetRequestSerializer, responses={204: None}, summary="Request a password reset email")
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # Do not reveal whether an email address has an account.
        return Response(status=status.HTTP_204_NO_CONTENT)


class PasswordResetConfirmAPIView(APIView):
    permission_classes = (permissions.AllowAny,)

    @extend_schema(request=PasswordResetConfirmSerializer, responses={204: None}, summary="Set a new password using a reset token")
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user_id = force_str(urlsafe_base64_decode(serializer.validated_data["uid"]))
            user = get_user_model().objects.get(pk=user_id)
        except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
            return Response({"uid": ["Invalid reset link."]}, status=status.HTTP_400_BAD_REQUEST)
        if not default_token_generator.check_token(user, serializer.validated_data["token"]):
            return Response({"token": ["Invalid or expired reset token."]}, status=status.HTTP_400_BAD_REQUEST)
        password = serializer.validated_data["new_password"]
        from django.contrib.auth.password_validation import validate_password
        try:
            validate_password(password, user)
        except Exception as error:
            return Response({"new_password": list(error.messages)}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(password)
        user.save(update_fields=["password"])
        return Response(status=status.HTTP_204_NO_CONTENT)
