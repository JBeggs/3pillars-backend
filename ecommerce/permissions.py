"""
Permissions for e-commerce multi-tenant API.
"""
from rest_framework import permissions
from .models import EcommerceCompany


class IsCompanyOwnerOrReadOnly(permissions.BasePermission):
    """
    Permission to check if user owns the company or is read-only.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions for all authenticated users
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        
        # Write permissions only for company owner or superuser
        if isinstance(obj, EcommerceCompany):
            return obj.owner == request.user or request.user.is_superuser
        elif hasattr(obj, 'company'):
            return obj.company.owner == request.user or request.user.is_superuser
        
        return False


class IsCompanyMember(permissions.BasePermission):
    """
    Permission to check if user is a member of the company.
    For now, checks if user is owner. Can be extended to check company users.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, EcommerceCompany):
            return obj.owner == request.user or request.user.is_superuser
        elif hasattr(obj, 'company'):
            return obj.company.owner == request.user or request.user.is_superuser
        
        return False

