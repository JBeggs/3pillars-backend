"""
Custom permissions for news platform API.
"""
from rest_framework import permissions
from ecommerce.utils import get_company_from_request


class HasCompanyAccess(permissions.BasePermission):
    """
    Permission to check if user has access to the company in the request.
    For read operations (GET, HEAD, OPTIONS), allows access if company ID is provided.
    For write operations, requires authentication and company membership or appropriate role.
    """
    def has_permission(self, request, view):
        company = get_company_from_request(request)
        
        # For read operations (GET, HEAD, OPTIONS), always allow access
        # The queryset will handle filtering by company or returning empty
        if request.method in permissions.SAFE_METHODS:
            return True  # Allow read access - queryset handles filtering
        
        # For write operations, require company and authentication
        if not company:
            return False
        
        if not request.user.is_authenticated:
            return False
        
        # Check user owns or is member of company
        if company.owner == request.user:
            return True
        
        # Check if user is a member (if ManyToMany is set up)
        if hasattr(company, 'users') and request.user in company.users.all():
            return True
        
        # Allow authors, editors, admins, and business owners to create content (for news platform)
        # Check user profile role - authors and business owners should be able to create articles
        if hasattr(request.user, 'news_profile'):
            profile = request.user.news_profile
            if profile.role in ['admin', 'editor', 'author', 'business_owner']:
                return True
        
        # Business owners can edit their own businesses even if they don't own the company in header
        # The object-level permission (IsBusinessOwnerOrReadOnly) will check actual ownership
        # This allows business owners to pass HasCompanyAccess for Business operations
        if hasattr(request.user, 'news_profile'):
            profile = request.user.news_profile
            if profile.role == 'business_owner':
                # For Business operations, allow business owners to pass
                # Object-level permission will verify they own the business
                # Check if view has Business model in queryset
                try:
                    if hasattr(view, 'queryset') and view.queryset:
                        model_name = view.queryset.model.__name__
                        if model_name == 'Business':
                            return True
                except:
                    pass
        
        # Superusers can access any company
        if request.user.is_superuser:
            return True
        
        return False


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Object-level permission: only authors can edit their articles.
    Drafts can only be viewed by their author (or admin/editor).
    Business owners can also create and edit articles.
    """
    def has_permission(self, request, view):
        # Allow business owners and authors to create articles
        if request.method == 'POST' and request.user.is_authenticated:
            if hasattr(request.user, 'news_profile'):
                profile = request.user.news_profile
                if profile.role in ['admin', 'editor', 'author', 'business_owner']:
                    return True
        # For other methods, allow (object-level permission will handle restrictions)
        return True
    
    def has_object_permission(self, request, view, obj):
        # Check if this is a draft article
        is_draft = hasattr(obj, 'status') and obj.status == 'draft'
        
        # For draft articles, restrict read access
        if request.method in permissions.SAFE_METHODS and is_draft:
            # Drafts can only be viewed by their author, admin, or editor
            if hasattr(obj, 'author') and obj.author == request.user:
                return True
            
            # Admins and editors can view all drafts
            if hasattr(request.user, 'news_profile'):
                profile = request.user.news_profile
                if profile.role in ['admin', 'editor']:
                    return True
            
            # Company owner can view drafts
            if hasattr(obj, 'company') and obj.company.owner == request.user:
                return True
            
            return False
        
        # For published articles, read permissions for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only to author or company owner
        if hasattr(obj, 'author') and obj.author == request.user:
            return True
        
        # Company owner can edit
        if hasattr(obj, 'company') and obj.company.owner == request.user:
            return True
        
        # Check user profile role - allow business owners to edit their own articles
        if hasattr(request.user, 'news_profile'):
            profile = request.user.news_profile
            if profile.role in ['admin', 'editor', 'business_owner']:
                # Business owners can edit their own articles
                if profile.role == 'business_owner' and hasattr(obj, 'author') and obj.author == request.user:
                    return True
                # Admins and editors can edit any article
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

