"""Permisos basados en el perfil de usuario."""

from rest_framework.permissions import BasePermission


def profile_for(user):
    return getattr(user, 'perfil', None)


def role_for(user):
    profile = profile_for(user)
    return profile.rol if profile else None


def company_for(user):
    profile = profile_for(user)
    return profile.empresa if profile else None


class IsAdminRole(BasePermission):
    message = 'Esta operación requiere permisos de administrador.'

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and role_for(request.user) == 'admin'
        )


class HasCompany(BasePermission):
    message = 'Esta operación requiere un usuario vinculado a una empresa.'

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and company_for(request.user) is not None
        )
