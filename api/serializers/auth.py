"""
Authentication serializers.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """User serializer for auth responses."""
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'is_superuser', 'is_staff', 'is_active'
        ]
        read_only_fields = ['id', 'is_superuser', 'is_staff', 'is_active']


class TokenResponseSerializer(serializers.Serializer):
    """Token response serializer."""
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = UserSerializer()


class RefreshTokenSerializer(serializers.Serializer):
    """Refresh token request serializer."""
    refresh = serializers.CharField()


class RefreshTokenResponseSerializer(serializers.Serializer):
    """Refresh token response serializer."""
    access = serializers.CharField()
