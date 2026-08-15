from rest_framework import permissions


class IsStaffOrReadOnly(permissions.BasePermission):
    """Allow public catalogue reads, but restrict catalogue changes to staff."""

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS or bool(
            request.user and request.user.is_authenticated and request.user.is_staff
        )

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit or delete it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the product.
        return obj.owner == request.user
