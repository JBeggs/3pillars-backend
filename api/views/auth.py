"""
Authentication views for API.
Fail hard - explicit error handling, no silent failures.
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth import get_user_model, authenticate
from drf_spectacular.utils import extend_schema

from api.serializers.auth import (
    UserSerializer,
    RefreshTokenSerializer,
    RefreshTokenResponseSerializer,
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
        
        # Check if account is active
        if not user.is_active:
            return Response(
                {'error': 'User account is inactive. Please contact administrator.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Verify password before attempting token generation
        authenticated_user = authenticate(username=username, password=password)
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


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """User registration endpoint."""
    # TODO: Implement registration logic if needed
    # For now, return not implemented
    return Response(
        {'message': 'Registration not implemented. Use admin panel.'},
        status=status.HTTP_501_NOT_IMPLEMENTED
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
    # Get active users, excluding superusers
    users = User.objects.filter(is_active=True, is_superuser=False).order_by('username')
    
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)

