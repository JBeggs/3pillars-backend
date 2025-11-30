# FCM Notification Settings API

## Overview

Users can control which push notifications they receive through per-user notification settings. Each user has a settings record that controls different types of notifications.

## API Endpoints

### Get Current User's Settings
**GET** `/api/fcm/notification-settings/me/`

Get the current user's notification settings. Creates default settings if they don't exist.

**Authentication**: Required

**Response (200 OK)**:
```json
{
  "notifications_enabled": true,
  "notify_orders_created": true,
  "notify_orders_paid": true,
  "notify_orders_shipped": true,
  "notify_orders_delivered": true,
  "notify_orders_cancelled": true,
  "notify_tasks_assigned": true,
  "notify_tasks_created": true,
  "notify_tasks_completed": false,
  "notify_tasks_due_soon": true,
  "notify_chat_messages": true,
  "notify_deals_created": true,
  "notify_deals_updated": true,
  "notify_deals_won_lost": true,
  "notify_payments_success": true,
  "notify_payments_failed": true,
  "created_at": "2024-01-15T10:00:00Z",
  "updated_at": "2024-01-15T10:00:00Z"
}
```

---

### Update Current User's Settings
**PUT** `/api/fcm/notification-settings/me/` or **PATCH** `/api/fcm/notification-settings/me/`

Update the current user's notification settings.

**Authentication**: Required

**Request Body** (PATCH - partial update):
```json
{
  "notify_chat_messages": false,
  "notify_tasks_completed": true
}
```

**Request Body** (PUT - full update):
```json
{
  "notifications_enabled": true,
  "notify_orders_created": true,
  "notify_orders_paid": true,
  "notify_orders_shipped": true,
  "notify_orders_delivered": true,
  "notify_orders_cancelled": true,
  "notify_tasks_assigned": true,
  "notify_tasks_created": true,
  "notify_tasks_completed": false,
  "notify_tasks_due_soon": true,
  "notify_chat_messages": true,
  "notify_deals_created": true,
  "notify_deals_updated": true,
  "notify_deals_won_lost": true,
  "notify_payments_success": true,
  "notify_payments_failed": true
}
```

**Response (200 OK)**:
```json
{
  // Updated settings object
}
```

---

## Notification Types

When sending notifications via `fcm_service.send_to_user()`, you can specify a `notification_type` parameter. The service will check the user's settings before sending:

```python
from fcm.services import fcm_service

# This will check user settings for 'order_created' before sending
fcm_service.send_to_user(
    user=user,
    title='New Order',
    body=f'Order {order.order_number} has been placed',
    data={'type': 'order', 'order_id': str(order.id)},
    notification_type='order_created'  # Checks user settings
)
```

### Available Notification Types

- `order_created` - New order created
- `order_paid` - Order payment confirmed
- `order_shipped` - Order shipped
- `order_delivered` - Order delivered
- `order_cancelled` - Order cancelled
- `task_assigned` - Task assigned to user
- `task_created` - New task created (if user is responsible)
- `task_completed` - Task completed (if user created it)
- `task_due_soon` - Task approaching due date
- `chat_message` - New chat message received
- `deal_created` - Deal created (if user is assigned)
- `deal_updated` - Deal updated (if user is assigned)
- `deal_won_lost` - Deal won or lost
- `payment_success` - Payment successful
- `payment_failed` - Payment failed

## Settings Behavior

1. **Master Switch**: If `notifications_enabled` is `False`, no notifications are sent regardless of individual settings.

2. **Default Values**: All notification types default to `True` except:
   - `notify_tasks_completed` defaults to `False`

3. **Automatic Creation**: Settings are automatically created when:
   - User first accesses their settings via API
   - FCM service checks settings for a user

## Flutter App Integration

### Get Settings
```dart
final response = await api.get('/api/fcm/notification-settings/me/');
final settings = NotificationSettings.fromJson(response);
```

### Update Settings
```dart
await api.patch('/api/fcm/notification-settings/me/', {
  'notify_chat_messages': false,
  'notify_tasks_completed': true,
});
```

## Example Usage

### Disable All Notifications
```json
PUT /api/fcm/notification-settings/me/
{
  "notifications_enabled": false
}
```

### Enable Only Task Notifications
```json
PATCH /api/fcm/notification-settings/me/
{
  "notifications_enabled": true,
  "notify_orders_created": false,
  "notify_orders_paid": false,
  "notify_orders_shipped": false,
  "notify_orders_delivered": false,
  "notify_orders_cancelled": false,
  "notify_chat_messages": false,
  "notify_deals_created": false,
  "notify_deals_updated": false,
  "notify_deals_won_lost": false,
  "notify_payments_success": false,
  "notify_payments_failed": false
}
```

