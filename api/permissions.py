"""
Custom permissions for API endpoints.
Fail hard - explicit permission checks, no silent failures.
"""
from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Object-level permission: only owners can edit their objects."""
    
    def has_object_permission(self, request, view, obj):
        # Read permissions for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only to owner
        if not hasattr(obj, 'owner'):
            return False
        
        return obj.owner == request.user


class IsDepartmentMember(permissions.BasePermission):
    """Permission based on department/group membership."""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Allow authenticated users (groups are used for filtering in queryset, not permission)
        return True


class IsOwnerOrCoOwner(permissions.BasePermission):
    """Allow access if user is owner or co_owner."""
    
    def has_object_permission(self, request, view, obj):
        # Read permissions for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Check owner
        if hasattr(obj, 'owner') and obj.owner == request.user:
            return True
        
        # Check co_owner
        if hasattr(obj, 'co_owner') and obj.co_owner == request.user:
            return True
        
        return False


class IsResponsibleOrOwner(permissions.BasePermission):
    """For tasks: allow if user is responsible, owner, or co_owner."""
    
    def has_object_permission(self, request, view, obj):
        # Read permissions for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Check owner
        if hasattr(obj, 'owner') and obj.owner == request.user:
            return True
        
        # Check co_owner
        if hasattr(obj, 'co_owner') and obj.co_owner == request.user:
            return True
        
        # Check responsible (ManyToMany)
        if hasattr(obj, 'responsible'):
            if request.user in obj.responsible.all():
                return True
        
        return False

