"""
Authentication views for API.
Fail hard - explicit error handling, no silent failures.
"""
import logging
from rest_framework import status

logger = logging.getLogger(__name__)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth import get_user_model, authenticate
from django.db.utils import OperationalError, ProgrammingError
from drf_spectacular.utils import extend_schema

from api.serializers.auth import (
    UserSerializer,
    RefreshTokenSerializer,
    RefreshTokenResponseSerializer,
    BusinessRegistrationSerializer,
    UserRegistrationSerializer,
)

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom login view that returns user data with tokens."""
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        username = request.data.get('username', '').strip()
        password = request.data.get('password', '')
        
        # Validate input
        if not username:
            return Response(
                {'error': 'Username is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not password:
            return Response(
                {'error': 'Password is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user exists
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                {'error': 'Invalid username or password'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        except (OperationalError, ProgrammingError) as e:
            return Response(
                {'error': 'Database connection error. Please try again later.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        # Check if account is active
        if not user.is_active:
            return Response(
                {'error': 'User account is inactive. Please contact administrator.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Verify password before attempting token generation
        try:
            authenticated_user = authenticate(username=username, password=password)
        except (OperationalError, ProgrammingError) as e:
            return Response(
                {'error': 'Database connection error. Please try again later.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        if not authenticated_user:
            return Response(
                {'error': 'Invalid username or password'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Try to get tokens
        try:
            response = super().post(request, *args, **kwargs)
            
            if response.status_code == 200:
                try:
                    user = User.objects.get(username=username)
                    user_data = UserSerializer(user).data
                    response.data['user'] = user_data
                    
                    # Get user's company if available
                    from ecommerce.models import EcommerceCompany
                    # First try: user's owned company (for business owners)
                    company = EcommerceCompany.objects.filter(owner=user).first()
                    # Second try: user is a member of a company (for regular users)
                    if not company:
                        company = EcommerceCompany.objects.filter(users=user).first()
                    # Third try: Riverside Herald (for regular users who don't have a company yet)
                    if not company:
                        company = EcommerceCompany.objects.filter(
                            name__iexact='Riverside Herald'
                        ).first() or EcommerceCompany.objects.filter(
                            slug__iexact='riverside-herald'
                        ).first()
                        # If found, add user as member
                        if company and hasattr(company, 'users'):
                            company.users.add(user)
                    
                    if company:
                        response.data['company'] = {
                            'id': str(company.id),
                            'name': company.name,
                            'slug': company.slug,
                            'email': company.email,
                        }
                    
                    # Get news profile if it exists
                    try:
                        from news.models import Profile
                        profile = Profile.objects.get(user=user)
                        response.data['profile'] = {
                            'role': profile.role,
                            'is_verified': profile.is_verified,
                        }
                    except:
                        pass  # Profile might not exist yet
                except (OperationalError, ProgrammingError) as e:
                    return Response(
                        {'error': 'Database connection error. Please try again later.'},
                        status=status.HTTP_503_SERVICE_UNAVAILABLE
                    )
                except Exception as e:
                    return Response(
                        {'error': f'Error retrieving user data: {str(e)}'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
            elif response.status_code == 401:
                # Check response data for specific error
                error_detail = response.data.get('detail', '')
                if 'No active account' in str(error_detail):
                    return Response(
                        {'error': 'User account is inactive. Please contact administrator.'},
                        status=status.HTTP_401_UNAUTHORIZED
                    )
                return Response(
                    {'error': 'Invalid username or password'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            return response
            
        except (InvalidToken, TokenError) as e:
            return Response(
                {'error': f'Authentication failed: {str(e)}'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        except Exception as e:
            return Response(
                {'error': f'Login failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema(
    request=BusinessRegistrationSerializer,
    responses={
        201: {
            'type': 'object',
            'properties': {
                'message': {'type': 'string'},
                'user': UserSerializer,
                'company': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'string'},
                        'name': {'type': 'string'},
                        'slug': {'type': 'string'},
                        'email': {'type': 'string'},
                    }
                },
                'tokens': {
                    'type': 'object',
                    'properties': {
                        'access': {'type': 'string'},
                        'refresh': {'type': 'string'},
                    }
                }
            }
        },
        400: {'type': 'object', 'properties': {'error': {'type': 'string'}}},
    },
    operation_id='register_business',
    summary='Register a new business',
    description='Register a new small business account with company details. Creates both user and EcommerceCompany.',
)
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    Registration endpoint - handles both user and business registration.
    - If 'company_name' is provided: Business registration (creates new company)
    - Otherwise: User registration (connects to Riverside Herald)
    """
    # Detect registration type based on presence of company_name
    is_business_registration = 'company_name' in request.data and request.data.get('company_name')
    
    if is_business_registration:
        # Business registration - creates new company
        serializer = BusinessRegistrationSerializer(data=request.data)
    else:
        # User registration - connects to Riverside Herald
        serializer = UserRegistrationSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(
            {'error': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        result = serializer.save()
        user = result['user']
        company = result['company']
        
        # Generate tokens for immediate login
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        
        # Get news profile if it exists
        from news.models import Profile
        try:
            profile = Profile.objects.get(user=user)
            profile_data = {
                'role': profile.role,
                'is_verified': profile.is_verified,
            }
        except Profile.DoesNotExist:
            profile_data = None
        
        # Return user data, company data, and tokens
        response_data = {
            'message': 'Registration successful!' if not is_business_registration else 'Registration successful. Your account is pending approval. You will be notified once approved.',
            'user': UserSerializer(user).data,
            'company': {
                'id': str(company.id),
                'name': company.name,
                'slug': company.slug,
                'email': company.email,
                'status': company.status,
            },
            'tokens': {
                'access': access_token,
                'refresh': refresh_token,
            },
        }
        
        if profile_data:
            response_data['profile'] = profile_data
        
        if is_business_registration:
            response_data['pending_approval'] = True
        
        return Response(response_data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Registration error: {e}", exc_info=True)
        return Response(
            {'error': f'Registration failed: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    request=RefreshTokenSerializer,
    responses={
        200: RefreshTokenResponseSerializer,
        400: {'type': 'object', 'properties': {'error': {'type': 'string'}}},
    },
    operation_id='refresh_token',
    summary='Refresh access token',
    description='Refresh an expired access token using a valid refresh token',
)
@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token_view(request):
    """Token refresh endpoint."""
    refresh_token_value = request.data.get('refresh')
    
    if not refresh_token_value:
        return Response(
            {'error': 'Refresh token is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        token = RefreshToken(refresh_token_value)
        return Response({
            'access': str(token.access_token),
        })
    except Exception as e:
        return Response(
            {'error': f'Token refresh failed: {str(e)}'},
            status=status.HTTP_400_BAD_REQUEST
        )

# Alias for consistency
refresh_token = refresh_token_view


@extend_schema(
    responses={200: UserSerializer(many=True)},
    operation_id='list_users',
    summary='List users',
    description='Get list of active users (excluding admin/superuser)',
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_users(request):
    """List users endpoint - excludes admin/superuser."""
    User = get_user_model()
    try:
        # Get active users, excluding superusers
        users = User.objects.filter(is_active=True, is_superuser=False).order_by('username')
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    except (OperationalError, ProgrammingError) as e:
        return Response(
            {'error': 'Database connection error. Please try again later.'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )

