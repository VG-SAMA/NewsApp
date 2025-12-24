"""
Custom API permission classes for Django REST Framework.

Includes:
- IsReader: Grants access only to authenticated users with the 'reader' role.
"""

from rest_framework import permissions


class IsReader(permissions.BasePermission):
    """
    Permission class to allow only authenticated readers.

    Usage:
        Add to a DRF view's `permission_classes` list to restrict access to readers.

    Example:
        from .permissions import IsReader

        class ArticleListView(APIView):
            permission_classes = [IsReader]
    """

    def has_permission(self, request, view):
        """
        Check if the user is authenticated and has the role 'reader'.

        Args:
            request: DRF Request object.
            view: DRF View object.

        Returns:
            bool: True if user is authenticated and is a reader, False otherwise.
        """

        return request.user.is_authenticated and request.user.role == 'reader'
