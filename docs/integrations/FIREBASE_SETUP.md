# Firebase Setup Guide

This guide explains how to set up Firebase for both the Flutter app and Django backend.

## Overview

Firebase is used for push notifications (FCM - Firebase Cloud Messaging) to send notifications from the Django backend to the Flutter mobile app.

## Flutter App Setup ✅

### Already Configured:
- ✅ Firebase SDK installed (`firebase_core`, `firebase_messaging`)
- ✅ `google-services.json` configured
- ✅ Gradle plugins configured
- ✅ Firebase initialized in `main.dart`
- ✅ Notification service ready

### Next Steps:
1. The app will automatically request notification permissions
2. FCM tokens will be generated automatically
3. Tokens need to be sent to the backend (see API integration below)

## Django Backend Setup

### 1. Install Firebase Admin SDK

```bash
cd django-crm
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install firebase-admin==6.5.0
```

### 2. Get Firebase Service Account Key

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project (`pillars-firebase`)
3. Go to **Project Settings** → **Service Accounts**
4. Click **Generate New Private Key**
5. Download the JSON file
6. Save it as `django-crm/firebase-service-account.json` (add to `.gitignore`!)

### 3. Configure Django Settings

Add to `django-crm/webcrm/settings.py`:

```python
# Firebase Configuration
FIREBASE_CREDENTIALS_PATH = os.path.join(BASE_DIR, 'firebase-service-account.json')
```

Or use environment variable:

```python
FIREBASE_CREDENTIALS_PATH = os.environ.get('FIREBASE_CREDENTIALS_PATH', None)
```

### 4. Run Migrations

```bash
python manage.py makemigrations fcm
python manage.py migrate
```

## API Integration

### Register Device Token (Flutter → Django)

**Endpoint**: `POST /api/fcm/devices/`

**Request**:
```json
{
  "token": "fcm_device_token_here",
  "platform": "android",
  "device_id": "optional_device_id",
  "device_name": "Samsung Galaxy S21"
}
```

**Response**:
```json
{
  "id": "uuid",
  "token": "fcm_device_token_here",
  "platform": "android",
  "is_active": true,
  "created_at": "2024-01-15T10:00:00Z"
}
```

### Send Notification (Django → Flutter)

**In Django code**:
```python
from fcm.services import fcm_service
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.get(username='john')

# Send to user
fcm_service.send_to_user(
    user=user,
    title='New Message',
    body='You have a new message from John',
    data={'type': 'message', 'message_id': '123'}
)
```

## Flutter App Integration

### Update Notification Service

In `flutter_crm/lib/services/notification_service.dart`, add token registration:

```dart
Future<void> registerToken() async {
  try {
    final token = await getToken();
    if (token != null) {
      // Send token to backend
      await api.post('/api/fcm/devices/', data: {
        'token': token,
        'platform': Platform.isAndroid ? 'android' : 'ios',
        'device_name': await _getDeviceName(),
      });
    }
  } catch (e) {
    print('Failed to register FCM token: $e');
  }
}
```

### Call on Login

In your auth provider, after successful login:

```dart
final notificationService = NotificationService();
await notificationService.initNotifications();
await notificationService.registerToken();
```

## Testing

### 1. Test Token Registration

```bash
curl -X POST http://192.168.1.100:8000/api/fcm/devices/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "token": "test_token_123",
    "platform": "android"
  }'
```

### 2. Test Sending Notification

In Django shell:

```python
python manage.py shell

from fcm.services import fcm_service
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.first()

fcm_service.send_to_user(
    user=user,
    title='Test Notification',
    body='This is a test notification',
    data={'test': True}
)
```

## Security Notes

1. **Never commit `firebase-service-account.json`** to Git
2. Add to `.gitignore`:
   ```
   firebase-service-account.json
   ```
3. Use environment variables for production
4. Store credentials securely on PythonAnywhere

## Troubleshooting

### "firebase-admin not installed"
```bash
pip install firebase-admin==6.5.0
```

### "Failed to initialize Firebase Admin SDK"
- Check that `firebase-service-account.json` exists
- Verify the JSON file is valid
- Check file permissions

### "Token is unregistered"
- Token may have expired
- Device may have uninstalled the app
- Token will be automatically marked as inactive

### Notifications not received
1. Check device token is registered in Django admin
2. Verify token is active
3. Check Firebase Console for delivery status
4. Ensure app has notification permissions

## Production Deployment

### PythonAnywhere

1. Upload `firebase-service-account.json` to your home directory
2. Set environment variable in `.env`:
   ```env
   FIREBASE_CREDENTIALS_PATH=/home/yourusername/firebase-service-account.json
   ```
3. Restart web app

## Next Steps

1. ✅ Install firebase-admin
2. ✅ Download service account key
3. ✅ Configure settings
4. ✅ Run migrations
5. ⏳ Update Flutter app to register tokens
6. ⏳ Test sending notifications

