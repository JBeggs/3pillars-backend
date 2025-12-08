# Django CRM Investigation Report
## Product Management & API Key Integration for JavaMellow

**Date**: 2024  
**Purpose**: Investigate current state and plan implementation for product management endpoints and API key retrieval from tenant settings

---

## 📊 Current State Analysis

### ✅ What's Already Implemented

#### 1. **Multi-Tenant Architecture**
- ✅ `EcommerceCompany` model - fully implemented with all required fields
- ✅ `CompanyIntegrationSettings` model - stores Yoco and Pudo/Courier Guy API keys per company
- ✅ Company isolation via `get_company_from_request()` utility
- ✅ Company context from `X-Company-Id` header or user's owned company

#### 2. **Product Models**
- ✅ `EcommerceProduct` - complete model matching specification
- ✅ `Category` - company-scoped categories
- ✅ `ProductImage` - image management with company organization
- ✅ All required fields: pricing, inventory, SEO, dimensions, etc.

#### 3. **Cart & Order Models**
- ✅ `Cart` and `CartItem` - fully implemented
- ✅ `Order` and `OrderItem` - fully implemented
- ✅ Pudo pickup point support in Cart and Order models
- ✅ Delivery method choices include 'pudo'

#### 4. **Integration Services**
- ✅ `YocoService` - complete service class with:
  - `create_checkout_session()` method
  - `verify_webhook_signature()` method
  - `get_payment_status()` method
  - Credentials retrieved from `CompanyIntegrationSettings`
  
- ✅ `CourierGuyService` - service class with:
  - `search_pudo_locations()` method (placeholder - needs API implementation)
  - `create_shipment()` method
  - `track_shipment()` method
  - Credentials retrieved from `CompanyIntegrationSettings`

#### 5. **API Endpoints Structure**
- ✅ URL routing configured in `ecommerce/urls.py`
- ✅ ViewSets registered:
  - `EcommerceCompanyViewSet`
  - `EcommerceProductViewSet`
  - `CategoryViewSet`
  - `ProductImageViewSet`
  - `CartViewSet`
  - `OrderViewSet`
  - `PudoViewSet`
  - `PudoShipmentViewSet`
  - `YocoViewSet`
  - `YocoWebhookViewSet`
  - `SalesAnalyticsViewSet`

#### 6. **Permissions & Utilities**
- ✅ `IsCompanyOwnerOrReadOnly` permission
- ✅ `IsCompanyMember` permission
- ✅ `get_company_from_request()` utility
- ✅ `filter_by_company()` utility

---

## ❌ What Needs to Be Implemented

### 1. **Product Management Endpoints** (Priority: HIGH)

**Status**: ViewSet exists but needs verification and completion

**Required Endpoints** (from BACKEND_API_SPECIFICATION.md):
- ✅ `GET /api/v1/products/` - List products (exists)
- ✅ `GET /api/v1/products/:id` - Get product (exists)
- ✅ `GET /api/v1/products/slug/:slug` - Get by slug (needs verification)
- ✅ `POST /api/v1/products/` - Create product (exists)
- ✅ `PUT /api/v1/products/:id` - Update product (exists)
- ✅ `DELETE /api/v1/products/:id` - Delete product (exists)
- ❓ `POST /api/v1/products/bulk` - Bulk operations (needs verification)
- ❓ `POST /api/v1/products/images/upload` - Image upload (needs verification)
- ❓ `POST /api/v1/products/images/upload-multiple` - Multiple images (needs verification)
- ❓ `DELETE /api/v1/products/images/:imageId` - Delete image (needs verification)

**Action Items**:
1. Review `EcommerceProductViewSet` in `views.py` to ensure all endpoints match specification
2. Add missing endpoints if needed
3. Verify company scoping on all endpoints
4. Add bulk operations endpoint
5. Complete image upload endpoints

---

### 2. **API Key Retrieval from Tenant Settings** (Priority: HIGH)

**Status**: Services already retrieve from `CompanyIntegrationSettings` ✅

**Current Implementation**:
- ✅ `YocoService.__init__()` calls `_get_integration_settings()`
- ✅ `YocoService` uses `get_yoco_credentials()` method
- ✅ `CourierGuyService` uses `get_courier_guy_credentials()` method
- ✅ Both services automatically get company-specific credentials

**Verification Needed**:
1. ✅ Services correctly retrieve credentials per company
2. ✅ API endpoints use services correctly
3. ❓ Verify Yoco views use `YocoService` correctly
4. ❓ Verify Pudo views use `CourierGuyService` correctly

**Action Items**:
1. Review `views_yoco.py` to ensure it uses `YocoService`
2. Review `views_pudo.py` to ensure it uses `CourierGuyService`
3. Add error handling for missing credentials
4. Add validation that company has integration settings

---

### 3. **Management Command: Add Business Owner** (Priority: MEDIUM)

**Status**: Not implemented ❌

**Requirements**:
- Create a management command to add a business owner to the CRM
- Create `EcommerceCompany` with dummy data
- Create `User` account for the business owner
- Create `CompanyIntegrationSettings` with placeholder API keys
- Link company to owner

**Command Structure**:
```python
# ecommerce/management/commands/add_business_owner.py
python manage.py add_business_owner \
    --name "JavaMellow" \
    --email "owner@javamellow.com" \
    --username "javamellow_owner" \
    --password "secure_password"
```

**Dummy Data to Include**:
- Company name, slug, email
- Address (South African address)
- Business details (registration number, tax number)
- Settings (currency: ZAR, timezone: Africa/Johannesburg)
- Status: 'active', Plan: 'premium'
- Integration settings with placeholder API keys

**Action Items**:
1. Create `ecommerce/management/commands/` directory structure
2. Create `add_business_owner.py` command
3. Include dummy data for all required fields
4. Create integration settings with placeholder keys
5. Add helpful output messages

---

### 4. **Missing Endpoints Verification** (Priority: MEDIUM)

**Need to Check**:
1. **Product Endpoints**:
   - [ ] Verify `GET /api/v1/products/slug/:slug` exists
   - [ ] Verify bulk operations
   - [ ] Verify image upload endpoints

2. **Category Endpoints**:
   - [ ] Verify all CRUD operations exist
   - [ ] Verify company scoping

3. **Company Endpoints**:
   - [ ] Verify `GET /api/v1/companies/me` exists
   - [ ] Verify company management endpoints

---

## 🔍 Detailed Findings

### File Structure Analysis

```
django-crm/ecommerce/
├── models.py                    ✅ Complete - all models implemented
├── serializers.py              ❓ Need to verify completeness
├── views.py                    ❓ Need to verify all endpoints
├── views_cart.py               ✅ Exists
├── views_orders.py             ✅ Exists
├── views_yoco.py               ✅ Exists - needs verification
├── views_pudo.py               ✅ Exists - needs verification
├── views_analytics.py          ✅ Exists
├── services/
│   ├── yoco_service.py         ✅ Complete
│   └── courier_guy_service.py  ✅ Complete (needs API implementation)
├── permissions.py              ✅ Complete
├── utils.py                     ✅ Complete
└── urls.py                      ✅ Complete
```

### API Key Storage

**Model**: `CompanyIntegrationSettings`
- ✅ One-to-one relationship with `EcommerceCompany`
- ✅ Stores Yoco credentials: `yoco_secret_key`, `yoco_public_key`, `yoco_webhook_secret`
- ✅ Stores Courier Guy credentials: `courier_guy_api_key`, `courier_guy_api_secret`, `courier_guy_account_number`
- ✅ Helper methods: `get_yoco_credentials()`, `get_courier_guy_credentials()`
- ✅ Sandbox mode flags for both services

**Retrieval Pattern**:
```python
# Services automatically get credentials
yoco_service = YocoService(company)
# Internally calls: company.integration_settings.get_yoco_credentials()
```

---

## 📋 Implementation Plan

### Phase 1: Verification & Completion (Priority: HIGH)

1. **Review Existing Endpoints**
   - [ ] Read `views.py` completely
   - [ ] Verify all product endpoints match specification
   - [ ] Check image upload implementation
   - [ ] Verify bulk operations

2. **Complete Missing Endpoints**
   - [ ] Add `GET /products/slug/:slug` if missing
   - [ ] Add bulk operations endpoint
   - [ ] Complete image upload endpoints
   - [ ] Add image deletion endpoint

3. **Verify API Key Integration**
   - [ ] Review `views_yoco.py` - ensure uses `YocoService`
   - [ ] Review `views_pudo.py` - ensure uses `CourierGuyService`
   - [ ] Add error handling for missing credentials
   - [ ] Add validation for company integration settings

### Phase 2: Management Command (Priority: MEDIUM)

1. **Create Command Structure**
   - [ ] Create `ecommerce/management/` directory
   - [ ] Create `ecommerce/management/commands/` directory
   - [ ] Create `__init__.py` files

2. **Implement Command**
   - [ ] Create `add_business_owner.py`
   - [ ] Add command arguments (name, email, username, password)
   - [ ] Create User account
   - [ ] Create EcommerceCompany with dummy data
   - [ ] Create CompanyIntegrationSettings with placeholder keys
   - [ ] Link company to owner
   - [ ] Add success messages

3. **Dummy Data Template**
   ```python
   company_data = {
       'name': 'JavaMellow',
       'slug': 'javamellow',
       'email': 'contact@javamellow.com',
       'phone': '+27 12 345 6789',
       'address_street': '123 Main Street',
       'address_city': 'Pretoria',
       'address_province': 'Gauteng',
       'address_postal_code': '0001',
       'address_country': 'ZA',
       'registration_number': 'REG123456',
       'tax_number': 'VAT123456',
       'status': 'active',
       'plan': 'premium',
       'currency': 'ZAR',
       'timezone': 'Africa/Johannesburg',
       'language': 'en',
   }
   
   integration_settings = {
       'yoco_secret_key': 'sk_test_placeholder',
       'yoco_public_key': 'pk_test_placeholder',
       'yoco_webhook_secret': 'whsec_placeholder',
       'yoco_sandbox_mode': True,
       'courier_guy_api_key': 'api_key_placeholder',
       'courier_guy_api_secret': 'api_secret_placeholder',
       'courier_guy_account_number': 'ACC123456',
       'courier_guy_sandbox_mode': True,
   }
   ```

### Phase 3: Testing & Documentation (Priority: LOW)

1. **Testing**
   - [ ] Test product endpoints
   - [ ] Test API key retrieval
   - [ ] Test management command
   - [ ] Test company isolation

2. **Documentation**
   - [ ] Update API documentation
   - [ ] Document management command usage
   - [ ] Document API key setup process

---

## 🎯 Key Decisions Needed

1. **Image Upload Storage**
   - Current: `ProductImage` model stores URLs
   - Question: Where are images actually stored? (S3, Cloudinary, local media?)
   - Action: Verify image upload implementation

2. **Bulk Operations**
   - Question: What operations are needed? (update, delete, archive)
   - Action: Implement based on specification

3. **API Key Security**
   - Current: Stored in plain text in database
   - Question: Should we encrypt sensitive keys?
   - Action: Consider encryption for production

4. **Pudo API Integration**
   - Current: Placeholder implementation
   - Question: Actual Courier Guy API endpoints?
   - Action: Research actual API documentation

---

## 📝 Next Steps

1. **Immediate** (Before Coding):
   - [x] Complete investigation ✅
   - [ ] Review `views.py` to see what's implemented
   - [ ] Review `views_yoco.py` and `views_pudo.py`
   - [ ] Check serializers completeness

2. **Implementation**:
   - [ ] Complete missing product endpoints
   - [ ] Create management command
   - [ ] Verify API key integration
   - [ ] Add error handling

3. **Testing**:
   - [ ] Test all endpoints
   - [ ] Test management command
   - [ ] Test API key retrieval

---

## 🔗 Related Files to Review

1. `ecommerce/views.py` - Main product views
2. `ecommerce/views_yoco.py` - Yoco integration views
3. `ecommerce/views_pudo.py` - Pudo integration views
4. `ecommerce/serializers.py` - API serializers
5. `ecommerce/services/yoco_service.py` - Yoco service (already reviewed ✅)
6. `ecommerce/services/courier_guy_service.py` - Courier Guy service (already reviewed ✅)

---

**Report Status**: ✅ Complete - Ready for Implementation Review

**Recommendation**: Review existing views before implementing new code to avoid duplication.

