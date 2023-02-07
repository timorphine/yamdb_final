from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Кастомный пермишен, который расширит возможности встроенных пермишенов
    и разрешит полный доступ к объекту только админу(суперюзеру)"""

    def has_permission(self, request, view):

        user = request.user

        return (
            user.is_authenticated and user.is_admin
            or user.is_superuser
        )

    def has_object_permission(self, request, view, obj):

        user = request.user

        return (
            user.is_authenticated and user.is_admin
            or user.is_superuser
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    """Кастомный пермишен, который даст доступ на уровне админа"""

    def has_permission(self, request, view):

        return (
            request.method in permissions.SAFE_METHODS
            or (
                request.user.is_authenticated
                and request.user.is_admin
            )
        )


class UserIsAuthorOrReadOnly(permissions.BasePermission):
    """Кастомный пермишен, дающий доступ ко всем действиям только автору."""

    def has_object_permission(self, request, view, obj):

        return (
            obj.author == request.user
            or request.method in permissions.SAFE_METHODS
        )


class ReviewPermissions(permissions.BasePermission):
    """Кастомный пермишн для рецензий."""

    def has_permission(self, request, view):

        return (
            request.method in
            permissions.SAFE_METHODS or request.user
            and request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):

        if request.method in permissions.SAFE_METHODS:

            return True

        if request.user.is_authenticated:

            if request.method in [
                'PATCH',
                'DELETE'
            ]:

                return (
                    request.user.is_admin
                    or request.user.is_moderator
                    or obj.author == request.user
                )

            return True
