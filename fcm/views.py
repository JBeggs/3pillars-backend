"""
API views for FCM device registration and message sending.
"""
import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from .models import FCMDevice, FCMMessage, UserNotificationSettings
from .serializers import FCMDeviceSerializer, FCMMessageSerializer, UserNotificationSettingsSerializer
from .services import fcm_service

logger = logging.getLogger(__name__)


class FCMDeviceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for FCM device registration.
    """
    queryset = FCMDevice.objects.all()
    serializer_class = FCMDeviceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter devices by current user and company."""
        from ecommerce.utils import get_company_from_request
        company = get_company_from_request(self.request)
        queryset = FCMDevice.objects.filter(user=self.request.user)
        if company:
            queryset = queryset.filter(company=company)
        return queryset
    
    def perform_create(self, serializer):
        """Set user to current user (company handled in serializer)."""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['delete'], url_path='unregister')
    def unregister_device(self, request):
        """Unregister device token."""
        from ecommerce.utils import get_company_from_request
        token = request.data.get('token')
        if not token:
            return Response(
                {'error': 'Token is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        company = get_company_from_request(request)
        if not company:
            return Response(
                {'error': 'Company context required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            device = FCMDevice.objects.get(user=request.user, company=company, token=token)
            device.is_active = False
            device.save()
            return Response({'message': 'Device unregistered successfully'})
        except FCMDevice.DoesNotExist:
            return Response(
                {'error': 'Device not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class FCMMessageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing FCM messages (read-only).
    """
    queryset = FCMMessage.objects.all()
    serializer_class = FCMMessageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter messages by current user and company."""
        from ecommerce.utils import get_company_from_request
        company = get_company_from_request(self.request)
        queryset = FCMMessage.objects.filter(user=self.request.user)
        if company:
            queryset = queryset.filter(company=company)
        return queryset


class UserNotificationSettingsViewSet(viewsets.ModelViewSet):
    """
    ViewSet for user notification settings.
    Each user can only access their own settings.
    """
    serializer_class = UserNotificationSettingsSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter settings by current user and company."""
        from ecommerce.utils import get_company_from_request
        company = get_company_from_request(self.request)
        queryset = UserNotificationSettings.objects.filter(user=self.request.user)
        if company:
            queryset = queryset.filter(company=company)
        return queryset
    
    def get_object(self):
        """Get or create settings for current user and company."""
        from ecommerce.utils import get_company_from_request
        company = get_company_from_request(self.request)
        
        if not company:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({
                'company': 'Company context required. Provide X-Company-Id header or ensure user owns a company.'
            })
        
        settings, _ = UserNotificationSettings.objects.get_or_create(
            user=self.request.user,
            company=company
        )
        return settings
    
    def perform_create(self, serializer):
        """Set user to current user (company handled in serializer)."""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get', 'put', 'patch'], url_path='me')
    def my_settings(self, request):
        """Get or update current user's notification settings for current company."""
        from ecommerce.utils import get_company_from_request
        company = get_company_from_request(request)
        
        if not company:
            return Response(
                {'error': 'Company context required. Provide X-Company-Id header or ensure user owns a company.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        settings, created = UserNotificationSettings.objects.get_or_create(
            user=request.user,
            company=company
        )
        
        if request.method == 'GET':
            serializer = self.get_serializer(settings)
            return Response(serializer.data)
        
        # PUT or PATCH
        partial = request.method == 'PATCH'
        serializer = self.get_serializer(settings, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

