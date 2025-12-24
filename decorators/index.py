"""
Custom decorators for user group permissions.

This module provides a reusable decorator for restricting access to
Django views based on user group membership. It is used to enforce
role-based permissions such as Reader, Journalist, Editor, and
Publisher Manager access.

References:
https://stackoverflow.com/questions/5469159/how-to-create-a-custom-decorator-in-django
https://www.geeksforgeeks.org/python/creating-custom-decorator-in-django-for-different-permissions/
https://docs.djangoproject.com/en/5.2/topics/http/decorators/

"""

from django.core.exceptions import PermissionDenied
from functools import wraps


def group_required(group_name):
    """
    Decorator to allow access only to users belonging to a specific group.

    Args:
        group_name (str): Name of the group that is allowed access.

    Returns:
        function: Wrapped view function that checks user group membership.

    Raises:
        PermissionDenied: If the user is not authenticated or not in the group.
    """

    def decorator(view_func):
        """
        Wrap a view function with a group membership check.

        Args:
            view_func (Callable): The Django view function to wrap.

        Returns:
            Callable: Wrapped view function.
        """

        @wraps(view_func)
        def _wrapped_view_(request, *args, **kwargs):
            """
            Validate user authentication and group membership.

            Args:
                request (HttpRequest): The current request object.
                *args: Positional arguments passed to the view.
                **kwargs: Keyword arguments passed to the view.

            Returns:
                HttpResponse: The response from the wrapped view
                if access is granted.

            Raises:
                PermissionDenied: If the user is unauthenticated or
                not a member of the required group.
            """

            if (
                request.user.is_authenticated
                and request.user.groups.filter(name=group_name).exists()
            ):
                return view_func(request, *args, **kwargs)
            raise PermissionDenied

        return _wrapped_view_

    return decorator


# Role-based shortcut decorators
reader_required = group_required("Reader")
journalist_required = group_required("Journalist")
editor_required = group_required("Editor")
manager_publishers_required = group_required("Manage_Publishers")
