"""
Custom permissions for news platform API.
"""
from rest_framework import permissions
from ecommerce.utils import get_company_from_request


class HasCompanyAccess(permissions.BasePermission):
    """
    Permission to check if user has access to the company in the request.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        company = get_company_from_request(request)
        if not company:
            return False
        
        # Check user owns or is member of company
        if company.owner == request.user:
            return True
        
        # Check if user is a member (if ManyToMany is set up)
        if hasattr(company, 'users') and request.user in company.users.all():
            return True
        
        # Superusers can access any company
        if request.user.is_superuser:
            return True
        
        return False


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Object-level permission: only authors can edit their articles.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only to author or company owner
        if hasattr(obj, 'author') and obj.author == request.user:
            return True
        
        # Company owner can edit
        if hasattr(obj, 'company') and obj.company.owner == request.user:
            return True
        
        # Check user profile role
        if hasattr(request.user, 'news_profile'):
            profile = request.user.news_profile
            if profile.role in ['admin', 'editor']:
                return True
        
        return False


class IsBusinessOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission: only business owners can edit.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only to owner
        if hasattr(obj, 'owner') and obj.owner == request.user:
            return True
        
        # Company owner can edit
        if hasattr(obj, 'company') and obj.company.owner == request.user:
            return True
        
        return False

