# Multi-Tenant Setup Complete

## Summary

The Django CRM e-commerce system has been updated to be fully multi-tenant with company-scoped FCM notifications and payment/courier integrations.

## Changes Made

### 1. Company Context Extraction
- **Updated `ecommerce/utils.py`**: `get_company_from_request()` now extracts company from:
  1. `X-Company-Id` header (priority for web connections)
  2. Query parameter `company_id` (for superusers)
  3. User's owned company (fallback)

### 2. FCM Models - Company-Scoped
- **`FCMDevice`**: Added `company` ForeignKey, updated `unique_together` to `[user, company, token]`
- **`UserNotificationSettings`**: Changed from OneToOne to ForeignKey with `company`, updated `unique_together` to `[user, company]`
- **`FCMMessage`**: Added `company` ForeignKey for tracking

### 3. FCM Service & Views
- **`fcm/services.py`**: Updated `send_to_user()` to require `company` parameter
- **`fcm/views.py`**: All viewsets now filter by company from request
- **`fcm/serializers.py`**: Serializers extract company from request context

### 4. Company Integration Settings
- **New Model**: `CompanyIntegrationSettings` stores per-company:
  - Yoco credentials (secret key, public key, webhook secret, sandbox mode)
  - Courier Guy credentials (API key, API secret, account number, sandbox mode)
  - Payment gateway settings (JSON field for future gateways)
  - Courier settings (JSON field for future couriers)

### 5. Payment Gateway Integration
- **New Service**: `YocoService` class in `ecommerce/services/yoco_service.py`
  - `create_checkout_session()` - Creates Yoco checkout
  - `verify_webhook_signature()` - Verifies webhook signatures
  - `get_payment_status()` - Gets payment status
- **Updated**: `ecommerce/views_yoco.py` uses `YocoService` instead of mock data

### 6. Courier Integration
- **New Service**: `CourierGuyService` class in `ecommerce/services/courier_guy_service.py`
  - `search_pudo_locations()` - Searches for Pudo pickup points
  - `create_shipment()` - Creates shipments
  - `track_shipment()` - Tracks shipments
- **Updated**: `ecommerce/views_pudo.py` uses `CourierGuyService` (with fallback to mock)

### 7. Company Membership
- **Updated**: `EcommerceCompany` model now has `users` ManyToManyField for company membership (in addition to owner)

## API Usage

### Company Context Header
All API requests should include:
```
X-Company-Id: <company-uuid>
```

### FCM Device Registration
```http
POST /api/fcm/devices/
X-Company-Id: <company-uuid>
Authorization: Bearer <token>
Content-Type: application/json

{
  "token": "fcm_device_token",
  "platform": "android",
  "device_name": "Samsung Galaxy"
}
```

### Notification Settings
```http
GET /api/fcm/notification-settings/me/
X-Company-Id: <company-uuid>
Authorization: Bearer <token>
```

### Yoco Checkout
```http
POST /api/v1/orders/{order_id}/yoco-checkout
X-Company-Id: <company-uuid>
Authorization: Bearer <token>
Content-Type: application/json

{
  "successUrl": "https://example.com/success",
  "cancelUrl": "https://example.com/cancel"
}
```

### Pudo Locations
```http
GET /api/v1/pudo/locations?postalCode=0157&city=Centurion
X-Company-Id: <company-uuid>
Authorization: Bearer <token>
```

## Next Steps

### 1. Create Migrations
```bash
cd django-crm
source venv/bin/activate
python manage.py makemigrations ecommerce
python manage.py makemigrations fcm
python manage.py migrate
```

### 2. Configure Company Integration Settings
For each company, configure:
- Yoco API credentials (secret key, public key, webhook secret)
- Courier Guy API credentials (API key, API secret, account number)
- Set sandbox/production mode

### 3. Update Yoco & Courier Guy API Integration
The service classes are ready but need:
- Actual API endpoint URLs (if different from placeholders)
- Correct authentication method (adjust headers if needed)
- Response format mapping (adjust `_transform_*` methods if needed)

### 4. Test
- Test company context extraction from headers
- Test FCM device registration per company
- Test notification settings per company
- Test Yoco checkout creation
- Test Courier Guy shipment creation

## Files Changed

### Models
- `ecommerce/models.py` - Added `CompanyIntegrationSettings`, updated `EcommerceCompany`
- `fcm/models.py` - Made all models company-scoped

### Services
- `ecommerce/services/yoco_service.py` - New Yoco service
- `ecommerce/services/courier_guy_service.py` - New Courier Guy service
- `ecommerce/services/__init__.py` - Service exports

### Views
- `ecommerce/utils.py` - Updated company extraction
- `ecommerce/views_yoco.py` - Uses YocoService
- `ecommerce/views_pudo.py` - Uses CourierGuyService
- `fcm/services.py` - Updated to require company
- `fcm/views.py` - Company-scoped filtering
- `fcm/serializers.py` - Company context extraction

### Admin
- `ecommerce/admin.py` - Added CompanyIntegrationSettings admin

## Security Notes

1. **API Keys**: Store in `CompanyIntegrationSettings` model (encrypt in production)
2. **Webhook Verification**: Always verify webhook signatures using company's webhook secret
3. **Company Isolation**: All queries filter by company to prevent data leakage
4. **Header Validation**: Validate `X-Company-Id` header and verify user has access to that company

## Future Enhancements

1. **Multiple Payment Gateways**: Add PayFast, PayStack, Stripe using same pattern
2. **Multiple Couriers**: Add Fastway, PostNet using same pattern
3. **Company Membership Model**: Expand `users` ManyToMany to include roles/permissions
4. **API Key Encryption**: Encrypt sensitive credentials in database
5. **Webhook Retry Logic**: Add retry mechanism for failed webhooks

