"""
Utility functions for e-commerce app.
"""
from django.contrib.auth import get_user_model
from .models import EcommerceCompany

User = get_user_model()


def get_user_company(user):
    """
    Get the company associated with a user.
    Priority:
    1. First company owned by the user (business owners)
    2. First company where user is a member (regular users)
    """
    if not user or not user.is_authenticated:
        return None
    
    if user.is_superuser:
        # Superusers can access any company via query params
        return None
    
    # Priority 1: Get first company owned by user (business owners)
    company = EcommerceCompany.objects.filter(owner=user).first()
    if company:
        return company
    
    # Priority 2: Get first company where user is a member (regular users)
    company = EcommerceCompany.objects.filter(users=user).first()
    return company


def get_company_from_request(request):
    """
    Extract company from request.
    Priority:
    1. From X-Company-Id header (for web connections from multiple businesses)
    2. From query parameter (for superusers)
    3. From user's owned company
    4. From JWT token (if implemented)
    """
    user = request.user
    
    if not user.is_authenticated:
        return None
    
    # Priority 1: From X-Company-Id header (for multi-tenant web connections)
    company_id_header = request.headers.get('X-Company-Id') or request.META.get('HTTP_X_COMPANY_ID')
    if company_id_header:
        try:
            company = EcommerceCompany.objects.get(id=company_id_header)
            # Verify user has access to this company (owner or member)
            if user.is_superuser or company.owner == user or company.users.filter(id=user.id).exists():
                return company
        except (EcommerceCompany.DoesNotExist, ValueError):
            pass
    
    # Priority 2: Superusers can specify company via query param
    if user.is_superuser:
        company_id = request.query_params.get('company_id')
        if company_id:
            try:
                return EcommerceCompany.objects.get(id=company_id)
            except (EcommerceCompany.DoesNotExist, ValueError):
                return None
    
    # Priority 3: Get user's company (first owned company)
    return get_user_company(user)


def filter_by_company(queryset, company):
    """
    Filter queryset by company.
    If company is None (superuser), return all.
    """
    if company is None:
        return queryset
    return queryset.filter(company=company)

