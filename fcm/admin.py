from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from crm.site.crmadminsite import crm_site
from .models import FCMDevice, FCMMessage, UserNotificationSettings


@admin.register(FCMDevice)
class FCMDeviceAdmin(admin.ModelAdmin):
    list_display = ['user', 'company', 'platform', 'device_name', 'is_active', 'created_at', 'last_used_at']
    list_filter = ['company', 'platform', 'is_active', 'created_at']
    search_fields = ['user__username', 'user__email', 'token', 'device_id', 'device_name', 'company__name']
    readonly_fields = ['id', 'created_at', 'updated_at', 'last_used_at']
    raw_id_fields = ['user', 'company']


@admin.register(FCMMessage)
class FCMMessageAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'company', 'device', 'status', 'created_at', 'sent_at']
    list_filter = ['company', 'status', 'created_at']
    search_fields = ['title', 'body', 'user__username', 'fcm_message_id', 'company__name']
    readonly_fields = ['id', 'created_at', 'sent_at']
    raw_id_fields = ['user', 'device', 'company']


@admin.register(UserNotificationSettings)
class UserNotificationSettingsAdmin(admin.ModelAdmin):
    list_display = ['user', 'company', 'notifications_enabled', 'updated_at']
    list_filter = ['company', 'notifications_enabled', 'created_at']
    search_fields = ['user__username', 'user__email', 'company__name']
    raw_id_fields = ['user', 'company']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        (None, {
            'fields': ('user', 'company', 'notifications_enabled')
        }),
        (_('Order Notifications'), {
            'fields': (
                'notify_orders_created',
                'notify_orders_paid',
                'notify_orders_shipped',
                'notify_orders_delivered',
                'notify_orders_cancelled',
            ),
            'classes': ('collapse',)
        }),
        (_('Task Notifications'), {
            'fields': (
                'notify_tasks_assigned',
                'notify_tasks_created',
                'notify_tasks_completed',
                'notify_tasks_due_soon',
            ),
            'classes': ('collapse',)
        }),
        (_('Other Notifications'), {
            'fields': (
                'notify_chat_messages',
                'notify_deals_created',
                'notify_deals_updated',
                'notify_deals_won_lost',
                'notify_payments_success',
                'notify_payments_failed',
            ),
            'classes': ('collapse',)
        }),
        (_('Metadata'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# Register all models to crm_site as well (for custom admin interface)
crm_site.register(FCMDevice, FCMDeviceAdmin)
crm_site.register(FCMMessage, FCMMessageAdmin)
crm_site.register(UserNotificationSettings, UserNotificationSettingsAdmin)


# Register all models to crm_site as well (for custom admin interface)
crm_site.register(FCMDevice, FCMDeviceAdmin)
crm_site.register(FCMMessage, FCMMessageAdmin)
crm_site.register(UserNotificationSettings, UserNotificationSettingsAdmin)

