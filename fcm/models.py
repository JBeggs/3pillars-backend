"""
FCM (Firebase Cloud Messaging) models for storing device tokens.
"""
import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class FCMDevice(models.Model):
    """
    Model to store FCM device tokens for push notifications.
    Company-scoped: Users can have different devices per company.
    """
    PLATFORM_CHOICES = [
        ('android', 'Android'),
        ('ios', 'iOS'),
        ('web', 'Web'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fcm_devices')
    company = models.ForeignKey(
        'ecommerce.EcommerceCompany',
        on_delete=models.CASCADE,
        related_name='fcm_devices',
        help_text='Company this device is registered for'
    )
    token = models.CharField(max_length=255, db_index=True)
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES, default='android')
    device_id = models.CharField(max_length=255, blank=True, null=True, help_text='Device identifier')
    device_name = models.CharField(max_length=255, blank=True, null=True, help_text='Device name/model')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_used_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('FCM Device')
        verbose_name_plural = _('FCM Devices')
        unique_together = [['user', 'company', 'token']]
        indexes = [
            models.Index(fields=['user', 'company', 'is_active']),
            models.Index(fields=['company', 'is_active']),
            models.Index(fields=['token']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.company.name} - {self.platform} ({self.token[:20]}...)"


class FCMMessage(models.Model):
    """
    Model to track sent FCM messages.
    Company-scoped for tracking and analytics.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    device = models.ForeignKey(FCMDevice, on_delete=models.CASCADE, related_name='messages', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fcm_messages', null=True, blank=True)
    company = models.ForeignKey(
        'ecommerce.EcommerceCompany',
        on_delete=models.CASCADE,
        related_name='fcm_messages',
        null=True,
        blank=True,
        help_text='Company context for this message'
    )
    title = models.CharField(max_length=255)
    body = models.TextField()
    data = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    fcm_message_id = models.CharField(max_length=255, blank=True, null=True, help_text='FCM message ID from response')
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = _('FCM Message')
        verbose_name_plural = _('FCM Messages')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'company', 'status']),
            models.Index(fields=['company', 'status']),
            models.Index(fields=['device', 'status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.status}"


class UserNotificationSettings(models.Model):
    """
    Model to store user notification preferences.
    Company-scoped: Users can have different notification settings per company.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notification_settings'
    )
    company = models.ForeignKey(
        'ecommerce.EcommerceCompany',
        on_delete=models.CASCADE,
        related_name='user_notification_settings'
    )
    
    # Global toggle - if False, no notifications are sent
    notifications_enabled = models.BooleanField(
        default=True,
        help_text='Master switch for all notifications'
    )
    
    # Order notifications
    notify_orders_created = models.BooleanField(
        default=True,
        help_text='Notify when new orders are created'
    )
    notify_orders_paid = models.BooleanField(
        default=True,
        help_text='Notify when orders are paid'
    )
    notify_orders_shipped = models.BooleanField(
        default=True,
        help_text='Notify when orders are shipped'
    )
    notify_orders_delivered = models.BooleanField(
        default=True,
        help_text='Notify when orders are delivered'
    )
    notify_orders_cancelled = models.BooleanField(
        default=True,
        help_text='Notify when orders are cancelled'
    )
    
    # Task notifications
    notify_tasks_assigned = models.BooleanField(
        default=True,
        help_text='Notify when tasks are assigned to you'
    )
    notify_tasks_created = models.BooleanField(
        default=True,
        help_text='Notify when new tasks are created (if you are responsible)'
    )
    notify_tasks_completed = models.BooleanField(
        default=False,
        help_text='Notify when tasks you created are completed'
    )
    notify_tasks_due_soon = models.BooleanField(
        default=True,
        help_text='Notify when tasks are approaching due date'
    )
    
    # Chat notifications
    notify_chat_messages = models.BooleanField(
        default=True,
        help_text='Notify when you receive new chat messages'
    )
    
    # Deal notifications
    notify_deals_created = models.BooleanField(
        default=True,
        help_text='Notify when deals are created (if you are assigned)'
    )
    notify_deals_updated = models.BooleanField(
        default=True,
        help_text='Notify when deals are updated (if you are assigned)'
    )
    notify_deals_won_lost = models.BooleanField(
        default=True,
        help_text='Notify when deals are won or lost'
    )
    
    # Payment notifications
    notify_payments_success = models.BooleanField(
        default=True,
        help_text='Notify when payments are successful'
    )
    notify_payments_failed = models.BooleanField(
        default=True,
        help_text='Notify when payments fail'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('User Notification Settings')
        verbose_name_plural = _('User Notification Settings')
        unique_together = [['user', 'company']]
        indexes = [
            models.Index(fields=['user', 'company']),
            models.Index(fields=['company', 'notifications_enabled']),
        ]
    
    def __str__(self):
        return f"Notification Settings for {self.user.username} - {self.company.name}"
    
    def should_notify(self, notification_type: str) -> bool:
        """
        Check if user should receive a specific notification type.
        
        Args:
            notification_type: One of the notification type constants
            
        Returns:
            True if notification should be sent, False otherwise
        """
        if not self.notifications_enabled:
            return False
        
        # Map notification types to settings fields
        type_mapping = {
            'order_created': self.notify_orders_created,
            'order_paid': self.notify_orders_paid,
            'order_shipped': self.notify_orders_shipped,
            'order_delivered': self.notify_orders_delivered,
            'order_cancelled': self.notify_orders_cancelled,
            'task_assigned': self.notify_tasks_assigned,
            'task_created': self.notify_tasks_created,
            'task_completed': self.notify_tasks_completed,
            'task_due_soon': self.notify_tasks_due_soon,
            'chat_message': self.notify_chat_messages,
            'deal_created': self.notify_deals_created,
            'deal_updated': self.notify_deals_updated,
            'deal_won_lost': self.notify_deals_won_lost,
            'payment_success': self.notify_payments_success,
            'payment_failed': self.notify_payments_failed,
        }
        
        return type_mapping.get(notification_type, True)  # Default to True if type not found
    
    @classmethod
    def get_or_create_for_user(cls, user, company):
        """Get or create notification settings for a user and company."""
        settings, created = cls.objects.get_or_create(user=user, company=company)
        return settings

