from django.contrib import admin
from .models import FCMDevice, FCMMessage


@admin.register(FCMDevice)
class FCMDeviceAdmin(admin.ModelAdmin):
    list_display = ['user', 'platform', 'device_name', 'is_active', 'created_at', 'last_used_at']
    list_filter = ['platform', 'is_active', 'created_at']
    search_fields = ['user__username', 'user__email', 'token', 'device_id', 'device_name']
    readonly_fields = ['id', 'created_at', 'updated_at', 'last_used_at']
    raw_id_fields = ['user']


@admin.register(FCMMessage)
class FCMMessageAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'device', 'status', 'created_at', 'sent_at']
    list_filter = ['status', 'created_at']
    search_fields = ['title', 'body', 'user__username', 'fcm_message_id']
    readonly_fields = ['id', 'created_at', 'sent_at']
    raw_id_fields = ['user', 'device']

