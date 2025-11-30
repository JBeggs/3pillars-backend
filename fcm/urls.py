"""
URL configuration for FCM API.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FCMDeviceViewSet, FCMMessageViewSet, UserNotificationSettingsViewSet

router = DefaultRouter()
router.register(r'devices', FCMDeviceViewSet, basename='fcm-device')
router.register(r'messages', FCMMessageViewSet, basename='fcm-message')
router.register(r'notification-settings', UserNotificationSettingsViewSet, basename='notification-settings')

urlpatterns = [
    path('', include(router.urls)),
]

