"""
FCM (Firebase Cloud Messaging) service for sending push notifications.
"""
import logging
from typing import Optional, Dict, Any, List
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone

try:
    import firebase_admin
    from firebase_admin import credentials, messaging
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    logging.warning("firebase-admin not installed. FCM functionality will be limited.")

from .models import FCMDevice, FCMMessage

User = get_user_model()
logger = logging.getLogger(__name__)


class FCMService:
    """
    Service for sending Firebase Cloud Messaging notifications.
    """
    
    def __init__(self):
        """Initialize Firebase Admin SDK if not already initialized."""
        if not FIREBASE_AVAILABLE:
            logger.error("firebase-admin package not installed. Install it with: pip install firebase-admin")
            return
        
        # Initialize Firebase Admin SDK
        if not firebase_admin._apps:
            try:
                # Try to get credentials from settings
                cred_path = getattr(settings, 'FIREBASE_CREDENTIALS_PATH', None)
                if cred_path:
                    cred = credentials.Certificate(cred_path)
                    firebase_admin.initialize_app(cred)
                else:
                    # Try to use default credentials (for Google Cloud environments)
                    firebase_admin.initialize_app()
                logger.info("Firebase Admin SDK initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Firebase Admin SDK: {e}")
    
    def send_to_token(
        self,
        token: str,
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None,
        device: Optional[FCMDevice] = None
    ) -> Optional[str]:
        """
        Send notification to a specific FCM token.
        
        Args:
            token: FCM device token
            title: Notification title
            body: Notification body
            data: Additional data payload
            device: FCMDevice instance (optional, for tracking)
        
        Returns:
            FCM message ID if successful, None otherwise
        """
        if not FIREBASE_AVAILABLE:
            logger.error("Firebase Admin SDK not available")
            return None
        
        try:
            # Create message
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                data=data or {},
                token=token,
            )
            
            # Send message
            response = messaging.send(message)
            logger.info(f"Successfully sent message to token: {response}")
            
            # Create FCMMessage record
            if device:
                FCMMessage.objects.create(
                    device=device,
                    user=device.user,
                    company=device.company,
                    title=title,
                    body=body,
                    data=data or {},
                    status='sent',
                    fcm_message_id=response,
                    sent_at=timezone.now()
                )
            
            return response
        except messaging.UnregisteredError:
            logger.warning(f"Token is unregistered: {token}")
            # Mark device as inactive
            if device:
                device.is_active = False
                device.save()
            return None
        except Exception as e:
            logger.error(f"Failed to send FCM message: {e}")
            # Create FCMMessage record with error
            if device:
                FCMMessage.objects.create(
                    device=device,
                    user=device.user,
                    company=device.company,
                    title=title,
                    body=body,
                    data=data or {},
                    status='failed',
                    error_message=str(e)
                )
            return None
    
    def send_to_user(
        self,
        user: User,
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None,
        notification_type: Optional[str] = None,
        company: Optional['EcommerceCompany'] = None
    ) -> List[str]:
        """
        Send notification to all active devices of a user for a specific company.
        Checks user notification settings before sending.
        
        Args:
            user: User instance
            title: Notification title
            body: Notification body
            data: Additional data payload
            notification_type: Type of notification (e.g., 'order_created', 'task_assigned')
                             Used to check user preferences
            company: EcommerceCompany instance (required for company-scoped notifications)
        
        Returns:
            List of FCM message IDs
        """
        if not company:
            logger.warning(f"Company context required for sending notification to {user.username}")
            return []
        
        # Check user notification settings for this company
        if notification_type:
            from .models import UserNotificationSettings
            settings = UserNotificationSettings.get_or_create_for_user(user, company)
            if not settings.should_notify(notification_type):
                logger.info(f"User {user.username} has disabled {notification_type} notifications for company {company.name}")
                return []
        
        # Get devices for user and company
        devices = FCMDevice.objects.filter(user=user, company=company, is_active=True)
        message_ids = []
        
        for device in devices:
            message_id = self.send_to_token(
                token=device.token,
                title=title,
                body=body,
                data=data,
                device=device
            )
            if message_id:
                message_ids.append(message_id)
        
        return message_ids
    
    def send_to_multiple_users(
        self,
        users: List[User],
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[int, List[str]]:
        """
        Send notification to multiple users.
        
        Args:
            users: List of User instances
            title: Notification title
            body: Notification body
            data: Additional data payload
        
        Returns:
            Dictionary mapping user IDs to list of message IDs
        """
        results = {}
        for user in users:
            message_ids = self.send_to_user(user, title, body, data)
            results[user.id] = message_ids
        return results
    
    def send_to_topic(
        self,
        topic: str,
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Send notification to a topic (all subscribed devices).
        
        Args:
            topic: Topic name
            title: Notification title
            body: Notification body
            data: Additional data payload
        
        Returns:
            FCM message ID if successful, None otherwise
        """
        if not FIREBASE_AVAILABLE:
            logger.error("Firebase Admin SDK not available")
            return None
        
        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                data=data or {},
                topic=topic,
            )
            
            response = messaging.send(message)
            logger.info(f"Successfully sent message to topic {topic}: {response}")
            return response
        except Exception as e:
            logger.error(f"Failed to send FCM message to topic {topic}: {e}")
            return None


# Singleton instance
fcm_service = FCMService()

