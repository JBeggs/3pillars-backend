# FCM Notification Integration Guide

## Current Status

**FCM messages are NOT automatically triggered.** The FCM service exists but needs to be integrated into business events.

## Where Notifications Should Be Triggered

### 1. Order Events
- **Order Created**: Notify company admins when a new order is placed
- **Order Paid**: Notify customer and company when payment is confirmed
- **Order Shipped**: Notify customer when order is shipped
- **Order Delivered**: Notify customer when order is delivered

### 2. Task Events
- **Task Assigned**: Notify user when assigned to a task
- **Task Created**: Notify responsible users when a new task is created
- **Task Completed**: Notify task owner when task is marked complete
- **Task Due Soon**: Notify users when task is approaching due date

### 3. Chat Messages
- **New Message**: Notify recipient when a new message is received
- **Message in Task/Deal**: Notify relevant users when message is posted

### 4. Deal Events
- **Deal Created**: Notify assigned users
- **Deal Status Changed**: Notify relevant users
- **Deal Won/Lost**: Notify team members

### 5. Payment Events
- **Payment Success**: Notify customer and company
- **Payment Failed**: Notify customer
- **Refund Processed**: Notify customer

## Implementation Options

### Option 1: Django Signals (Recommended)
Use Django signals to automatically trigger notifications when models are saved:

```python
# In fcm/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from ecommerce.models import Order
from fcm.services import fcm_service

@receiver(post_save, sender=Order)
def notify_order_created(sender, instance, created, **kwargs):
    if created:
        # Notify company admins
        company_admins = instance.company.users.filter(is_staff=True)
        for admin in company_admins:
            fcm_service.send_to_user(
                user=admin,
                title='New Order',
                body=f'Order {instance.order_number} has been placed',
                data={'type': 'order', 'order_id': str(instance.id)}
            )
```

### Option 2: Direct Calls in Views
Call FCM service directly in viewset methods:

```python
# In ecommerce/views_orders.py
def create_from_cart(self, request):
    # ... create order ...
    
    # Send notification
    if order.customer:
        fcm_service.send_to_user(
            user=order.customer,
            title='Order Confirmed',
            body=f'Your order {order.order_number} has been confirmed',
            data={'type': 'order', 'order_id': str(order.id)}
        )
```

### Option 3: Celery Tasks (For Async)
For better performance, use Celery to send notifications asynchronously:

```python
# In fcm/tasks.py
from celery import shared_task
from fcm.services import fcm_service

@shared_task
def send_order_notification(user_id, order_id):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    user = User.objects.get(id=user_id)
    order = Order.objects.get(id=order_id)
    
    fcm_service.send_to_user(
        user=user,
        title='New Order',
        body=f'Order {order.order_number} has been placed',
        data={'type': 'order', 'order_id': str(order.id)}
    )
```

## Next Steps

1. **Decide on integration approach** (signals vs direct calls vs Celery)
2. **Create signal handlers** for each event type
3. **Test notifications** for each event
4. **Update Flutter app** to handle notification taps and navigate to relevant screens

## Testing

To test FCM notifications manually:

```python
# In Django shell
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

