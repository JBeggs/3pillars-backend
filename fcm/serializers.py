"""
Serializers for FCM API.
"""
from rest_framework import serializers
from .models import FCMDevice, FCMMessage, UserNotificationSettings


class FCMDeviceSerializer(serializers.ModelSerializer):
    """Serializer for FCM Device registration."""
    
    class Meta:
        model = FCMDevice
        fields = ['id', 'token', 'platform', 'device_id', 'device_name', 'is_active', 'company', 'created_at', 'last_used_at']
        read_only_fields = ['id', 'created_at', 'last_used_at']
    
    def create(self, validated_data):
        """Create or update device token for current user and company."""
        user = self.context['request'].user
        token = validated_data['token']
        
        # Get company from request
        from ecommerce.utils import get_company_from_request
        request = self.context['request']
        company = get_company_from_request(request)
        
        if not company:
            raise serializers.ValidationError({
                'company': 'Company context required. Provide X-Company-Id header or ensure user owns a company.'
            })
        
        # Get or create device for user + company + token
        device, created = FCMDevice.objects.get_or_create(
            user=user,
            company=company,
            token=token,
            defaults=validated_data
        )
        
        # Update if exists
        if not created:
            for key, value in validated_data.items():
                setattr(device, key, value)
            device.is_active = True
            device.save()
        
        return device


class FCMMessageSerializer(serializers.ModelSerializer):
    """Serializer for FCM Message."""
    
    class Meta:
        model = FCMMessage
        fields = ['id', 'title', 'body', 'data', 'status', 'fcm_message_id', 'created_at', 'sent_at']
        read_only_fields = ['id', 'status', 'fcm_message_id', 'created_at', 'sent_at']


class UserNotificationSettingsSerializer(serializers.ModelSerializer):
    """Serializer for User Notification Settings."""
    
    class Meta:
        model = UserNotificationSettings
        fields = [
            'notifications_enabled',
            'notify_orders_created',
            'notify_orders_paid',
            'notify_orders_shipped',
            'notify_orders_delivered',
            'notify_orders_cancelled',
            'notify_tasks_assigned',
            'notify_tasks_created',
            'notify_tasks_completed',
            'notify_tasks_due_soon',
            'notify_chat_messages',
            'notify_deals_created',
            'notify_deals_updated',
            'notify_deals_won_lost',
            'notify_payments_success',
            'notify_payments_failed',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def create(self, validated_data):
        """Create settings for current user and company."""
        user = self.context['request'].user
        
        # Get company from request
        from ecommerce.utils import get_company_from_request
        request = self.context['request']
        company = get_company_from_request(request)
        
        if not company:
            raise serializers.ValidationError({
                'company': 'Company context required. Provide X-Company-Id header or ensure user owns a company.'
            })
        
        settings, _ = UserNotificationSettings.objects.get_or_create(
            user=user,
            company=company,
            defaults=validated_data
        )
        return settings

