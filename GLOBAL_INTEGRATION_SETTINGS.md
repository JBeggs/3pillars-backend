# Global Integration Settings Implementation

## Overview

This implementation adds global/system-wide Courier Guy and Yoco integration settings that serve as fallback defaults when company-specific settings are not configured. Companies can override these global settings with their own credentials.

## Architecture

### Global Settings (Fallback)
- **Model**: `GlobalIntegrationSettings`
- **Pattern**: Singleton (only one instance exists)
- **Purpose**: System-wide defaults for Courier Guy and Yoco credentials
- **Location**: Django Admin → E-commerce → Global Integration Settings

### Company Settings (Override)
- **Model**: `CompanyIntegrationSettings` (existing)
- **Pattern**: One per company
- **Purpose**: Company-specific credentials that override global settings
- **Behavior**: If company settings are blank, falls back to global settings

## How It Works

### Fallback Logic

1. **Company requests credentials** via `CompanyIntegrationSettings.get_yoco_credentials()` or `get_courier_guy_credentials()`
2. **Check company settings first**: If company has configured credentials, use those
3. **Fallback to global**: If company settings are blank/null, use global settings
4. **Error if both missing**: If neither company nor global settings exist, raise error

### Example Flow

```python
# Company has no Yoco settings configured
company_settings = CompanyIntegrationSettings.objects.get(company=company)
credentials = company_settings.get_yoco_credentials()
# Returns global Yoco credentials (if configured)

# Company has Yoco settings configured
company_settings.yoco_secret_key = "sk_company_123"
credentials = company_settings.get_yoco_credentials()
# Returns company-specific credentials
```

## Implementation Details

### 1. GlobalIntegrationSettings Model

**File**: `ecommerce/models.py`

- Singleton pattern (pk=1, prevents multiple instances)
- Same fields as CompanyIntegrationSettings for Courier Guy and Yoco
- Cannot be deleted (delete() method disabled)
- Helper method: `get_global_settings()` - gets or creates the singleton

### 2. Updated CompanyIntegrationSettings Methods

**File**: `ecommerce/models.py`

- `get_yoco_credentials()` - Checks company settings first, falls back to global
- `get_courier_guy_credentials()` - Checks company settings first, falls back to global
- Uses `GlobalIntegrationSettings.get_global_settings()` to access global settings

### 3. Service Classes Updated

**Files**: 
- `ecommerce/services/courier_guy_service.py`
- `ecommerce/services/yoco_service.py`

- Both services automatically use the fallback logic via `get_credentials()` methods
- Error messages updated to mention global settings option
- No changes needed to service logic - fallback is transparent

### 4. Admin Interface

**File**: `ecommerce/admin.py`

**GlobalIntegrationSettingsAdmin**:
- Singleton admin (prevents adding multiple instances)
- Prevents deletion
- Clear descriptions explaining these are fallback defaults

**CompanyIntegrationSettingsAdmin**:
- Updated fieldset descriptions
- Explains that blank fields will use global settings
- Clear indication of override behavior

## Usage

### Setting Up Global Settings

1. **Access Django Admin**: `/admin/ecommerce/globalintegrationsettings/`
2. **Create/Edit Global Settings**: Only one instance can exist
3. **Configure Credentials**:
   - Yoco: secret_key, public_key, webhook_secret, sandbox_mode
   - Courier Guy: api_key, api_secret, account_number, sandbox_mode
4. **Save**: These become the default for all companies

### Company Override

1. **Access Company Settings**: `/admin/ecommerce/companyintegrationsettings/`
2. **Select Company**: Choose the company to configure
3. **Override Global Settings**:
   - Fill in company-specific credentials to override global
   - Leave blank to use global settings
4. **Save**: Company now uses its own credentials

### In Code

```python
from ecommerce.models import EcommerceCompany, CompanyIntegrationSettings
from ecommerce.services import CourierGuyService, YocoService

# Get company
company = EcommerceCompany.objects.get(slug='javamellow')

# Courier Guy service automatically uses fallback
courier_service = CourierGuyService(company)
# Will use company settings if configured, otherwise global settings

# Yoco service automatically uses fallback
yoco_service = YocoService(company)
# Will use company settings if configured, otherwise global settings
```

## Migration

**File**: `ecommerce/migrations/0003_globalintegrationsettings.py`

Run migration:
```bash
python manage.py migrate ecommerce
```

This creates the `GlobalIntegrationSettings` table in the database.

## Benefits

1. **Centralized Management**: One place to configure default credentials
2. **Easy Onboarding**: New companies automatically use global settings
3. **Flexible Override**: Companies can use their own credentials when ready
4. **No Code Changes**: Services automatically use fallback - transparent to application code
5. **Backward Compatible**: Existing company-specific settings continue to work

## Testing

### Test Global Fallback

1. Create global settings with test credentials
2. Create company without integration settings
3. Use service - should use global credentials
4. Verify API calls work with global credentials

### Test Company Override

1. Create global settings with test credentials
2. Create company with different credentials
3. Use service - should use company credentials
4. Verify API calls work with company credentials

### Test Error Handling

1. Remove global settings (or leave blank)
2. Create company without integration settings
3. Use service - should raise clear error message
4. Error should mention configuring global or company settings

## Security Notes

- Global settings should be configured by system administrators only
- Company-specific settings override global (more secure for sensitive credentials)
- Consider encrypting sensitive fields in production
- Use environment variables for initial global setup in production

## Future Enhancements

- Add encryption for sensitive credential fields
- Add audit logging for credential changes
- Add API endpoint for companies to check which settings they're using
- Add validation to ensure at least global OR company settings exist

