# Multi-Tenancy Impact Analysis

## Current State

### What IS Multi-Tenant
1. **E-commerce App** (`ecommerce`):
   - Uses `EcommerceCompany` model
   - Products, Categories, Carts, Orders are company-scoped
   - Users associated via `EcommerceCompany.owner` field
   - Data isolation enforced in viewsets

### What is NOT Multi-Tenant (Yet)
1. **Main CRM** (`crm`, `tasks`, `chat`):
   - Uses ownership-based filtering (owner field, groups/departments)
   - NOT company-scoped
   - Users can see data based on ownership/groups, not company membership

2. **FCM Models** (just created):
   - `FCMDevice` - user-scoped only
   - `FCMMessage` - user-scoped only  
   - `UserNotificationSettings` - user-scoped only
   - **NO company association**

## Impact of Making System Fully Multi-Tenant

If the Django CRM is now fully multi-tenant, here's what needs to change:

---

## 1. FCM Models Need Company Association

### Current Problem
- FCM devices, messages, and settings are user-scoped only
- No way to isolate notifications by company
- Users in multiple companies would share settings

### Required Changes

#### Option A: Company-Scoped FCM (Recommended)
Make FCM models company-aware:

```python
# fcm/models.py
class FCMDevice(models.Model):
    user = models.ForeignKey(User, ...)
    company = models.ForeignKey('ecommerce.EcommerceCompany', ...)  # ADD THIS
    token = models.CharField(...)
    # ... rest of fields

class UserNotificationSettings(models.Model):
    user = models.ForeignKey(User, ...)
    company = models.ForeignKey('ecommerce.EcommerceCompany', ...)  # ADD THIS
    # ... rest of fields
    class Meta:
        unique_together = [['user', 'company']]  # One settings per user per company
```

**Impact:**
- Users can have different notification settings per company
- Devices registered per company
- Better isolation

#### Option B: User-Scoped (Current)
Keep as-is if:
- Users only belong to one company
- Settings should be global per user
- Simpler implementation

---

## 2. FCM Service Needs Company Context

### Current Problem
`fcm_service.send_to_user()` doesn't know which company context the notification is for.

### Required Changes

```python
# fcm/services.py
def send_to_user(
    self,
    user: User,
    title: str,
    body: str,
    data: Optional[Dict[str, Any]] = None,
    notification_type: Optional[str] = None,
    company: Optional['EcommerceCompany'] = None  # ADD THIS
) -> List[str]:
    # Get settings for user + company
    if company:
        settings = UserNotificationSettings.objects.get(
            user=user, company=company
        )
    else:
        settings = UserNotificationSettings.get_or_create_for_user(user)
    
    # Get devices for user + company
    devices = FCMDevice.objects.filter(
        user=user, 
        is_active=True,
        company=company  # If company-scoped
    )
```

---

## 3. API Endpoints Need Company Context

### Current Problem
- `/api/fcm/notification-settings/me/` doesn't know which company
- Settings are global, not per-company

### Required Changes

```python
# fcm/views.py
@action(detail=False, methods=['get', 'put', 'patch'], url_path='me')
def my_settings(self, request):
    # Get company from request (like ecommerce views do)
    from ecommerce.utils import get_company_from_request
    company = get_company_from_request(request)
    
    if not company:
        return Response(
            {'error': 'Company context required'},
            status=400
        )
    
    settings, created = UserNotificationSettings.objects.get_or_create(
        user=request.user,
        company=company  # Company-scoped
    )
    # ... rest of logic
```

---

## 4. Notification Triggers Need Company Context

When sending notifications from business events, need to pass company:

```python
# Example: Order created notification
from ecommerce.utils import get_user_company
from fcm.services import fcm_service

# In order creation view
company = order.company
fcm_service.send_to_user(
    user=company.owner,
    title='New Order',
    body=f'Order {order.order_number} has been placed',
    data={'type': 'order', 'order_id': str(order.id)},
    notification_type='order_created',
    company=company  # Pass company context
)
```

---

## 5. User-Company Association

### Current State
- Users associated with `EcommerceCompany` via `owner` field (one-to-many)
- No explicit "company membership" model
- Users can own multiple companies

### Questions to Answer
1. **Can users belong to multiple companies?**
   - If YES: Need company-scoped FCM models
   - If NO: Can keep user-scoped (simpler)

2. **How are users assigned to companies?**
   - Currently: Only via `EcommerceCompany.owner`
   - Need: Company membership model? Or keep owner-based?

3. **What about main CRM (tasks, deals, contacts)?**
   - Are these also company-scoped now?
   - Or still ownership-based?

---

## Recommended Implementation Plan

### Phase 1: Determine Scope
1. **Clarify multi-tenancy model:**
   - Is main CRM also multi-tenant?
   - Can users belong to multiple companies?
   - How is company context determined?

### Phase 2: Update FCM Models (If Company-Scoped)
1. Add `company` ForeignKey to:
   - `FCMDevice`
   - `UserNotificationSettings`
   - `FCMMessage` (optional, for tracking)

2. Update `unique_together` constraints:
   ```python
   # FCMDevice
   unique_together = [['user', 'company', 'token']]
   
   # UserNotificationSettings
   unique_together = [['user', 'company']]
   ```

3. Create migration

### Phase 3: Update FCM Service
1. Add `company` parameter to `send_to_user()`
2. Update settings lookup to include company
3. Update device lookup to include company

### Phase 4: Update API Endpoints
1. Extract company from request in viewsets
2. Update settings endpoints to be company-aware
3. Update device registration to include company

### Phase 5: Update Notification Triggers
1. Pass company context when sending notifications
2. Update all notification calls in:
   - Order views
   - Task views
   - Chat views
   - Deal views

---

## Migration Strategy

### If Adding Company to Existing Models

1. **Add nullable company field first:**
   ```python
   company = models.ForeignKey(
       'ecommerce.EcommerceCompany',
       null=True,
       blank=True,
       on_delete=models.CASCADE
   )
   ```

2. **Backfill data:**
   ```python
   # Migration data migration
   for device in FCMDevice.objects.filter(company__isnull=True):
       company = EcommerceCompany.objects.filter(owner=device.user).first()
       if company:
           device.company = company
           device.save()
   ```

3. **Make field required:**
   ```python
   company = models.ForeignKey(
       'ecommerce.EcommerceCompany',
       null=False,  # Now required
       on_delete=models.CASCADE
   )
   ```

---

## Testing Checklist

- [ ] Users can register devices per company
- [ ] Users can have different notification settings per company
- [ ] Notifications respect company-scoped settings
- [ ] Superusers can access all companies
- [ ] Regular users only see their company's data
- [ ] Migration handles existing data correctly

---

## Questions to Answer

1. **Is the main CRM (tasks, deals, contacts) also multi-tenant?**
   - If yes, need broader changes
   - If no, only e-commerce + FCM need changes

2. **Can users belong to multiple companies?**
   - Determines if FCM should be company-scoped

3. **How is company context determined?**
   - From JWT token?
   - From request headers?
   - From user's owned company?
   - From query parameters?

4. **What about users who don't own a company?**
   - Can they still use FCM?
   - How do they get assigned to a company?

