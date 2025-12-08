# Management Commands Guide
## Business Owner Setup & Database Reset

This guide explains the management commands created for the JavaMellow project.

---

## 📋 Available Commands

### 1. `add_business_owner` - Add Business Owner with Riverside Herald Access

**Purpose**: Creates a business owner with:
- User account
- EcommerceCompany (for e-commerce)
- CompanyIntegrationSettings (with placeholder API keys)
- Riverside Herald access (news Profile for content management)

**Usage**:
```bash
python manage.py add_business_owner \
    --email owner@javamellow.com \
    --name "JavaMellow" \
    --password "secure_password" \
    --full-name "John Doe"
```

**Options**:
- `--email` (required): Business owner email address
- `--name`: Company name (default: "JavaMellow")
- `--username`: Username (default: email prefix)
- `--password`: Password (default: "changeme123")
- `--full-name`: Full name (default: "Business Owner")
- `--phone`: Phone number (default: "+27 12 345 6789")
- `--city`: City (default: "Pretoria")
- `--province`: Province (default: "Gauteng")
- `--postal-code`: Postal code (default: "0001")

**What It Creates**:
1. ✅ User account (with staff access)
2. ✅ EcommerceCompany (business company)
3. ✅ CompanyIntegrationSettings (with placeholder Yoco & Pudo keys)
4. ✅ Riverside Herald company (if doesn't exist)
5. ✅ News Profile (role: business_owner) for Riverside Herald access
6. ✅ User added as member of Riverside Herald company

**Example Output**:
```
Creating business owner...
✓ Created user: owner@javamellow.com (owner)
✓ Created company: JavaMellow (ID: 550e8400-...)
✓ Created integration settings with placeholder API keys
✓ Found Riverside Herald company: Riverside Herald
✓ Added user as member of Riverside Herald company
✓ Created news profile with role: business_owner

✅ Setup complete!
```

---

### 2. `reset_database` - Reset Database

**Purpose**: Completely resets the database (drops all tables/data) and optionally repopulates.

**⚠️ WARNING**: This will DELETE ALL DATA!

**Usage**:

**Option 1: Flush Only (Safer - keeps structure)**
```bash
python manage.py reset_database --flush-only --repopulate
```

**Option 2: Complete Reset (Drops and recreates database)**
```bash
python manage.py reset_database --repopulate
```

**Options**:
- `--no-input`: Skip confirmation prompt (use with caution!)
- `--repopulate`: Repopulate database after reset (runs setupdata)
- `--skip-migrations`: Skip running migrations after reset
- `--flush-only`: Use Django flush instead of dropping database (safer)

**What It Does**:

**With `--flush-only`**:
1. Flushes all data (keeps database structure)
2. Runs migrations (if not skipped)
3. Repopulates (if `--repopulate` is used)

**Without `--flush-only`**:
1. Drops entire database
2. Creates new database
3. Runs migrations
4. Repopulates (if `--repopulate` is used)

**Database Support**:
- ✅ SQLite (deletes database file)
- ✅ MySQL (drops and recreates database)
- ✅ PostgreSQL (drops and recreates database)

**Safety Features**:
- Confirmation prompt (unless `--no-input`)
- Production environment warning (if DEBUG=False)
- Requires typing "DELETE ALL DATA" in production

---

## 🚀 Quick Start Workflow

### Initial Setup

```bash
# 1. Reset database (if needed)
python manage.py reset_database --flush-only --repopulate

# 2. Create business owner
python manage.py add_business_owner \
    --email owner@javamellow.com \
    --name "JavaMellow" \
    --password "secure_password123" \
    --full-name "John Doe"

# 3. Update API keys (via Django admin or API)
# - Yoco secret key
# - Yoco public key
# - Courier Guy API keys
```

### Reset and Repopulate

```bash
# Complete reset with repopulation
python manage.py reset_database --repopulate

# Then add business owner
python manage.py add_business_owner --email owner@javamellow.com
```

---

## 📝 Command Details

### `add_business_owner` Details

**Created Models**:
- `User` - Django user account
- `EcommerceCompany` - Business company (for e-commerce)
- `CompanyIntegrationSettings` - API keys storage
- `Profile` (news app) - For Riverside Herald content access

**Riverside Herald Integration**:
- Finds or creates "Riverside Herald" company
- Adds user as member of Riverside Herald company
- Creates news Profile with `business_owner` role
- User can now log into Riverside Herald and manage content

**Placeholder API Keys**:
- Yoco: `sk_test_placeholder_replace_with_real_key`
- Yoco Public: `pk_test_placeholder_replace_with_real_key`
- Courier Guy: `api_key_placeholder_replace_with_real_key`
- **Remember to update these with real keys!**

---

### `reset_database` Details

**Flush Method** (`--flush-only`):
- Uses Django's `flush` command
- Deletes all data but keeps database structure
- Safer for development
- Works with all database types

**Drop Method** (default):
- Drops entire database
- Creates fresh database
- More thorough reset
- Requires database admin privileges

**Repopulation**:
- Runs `setupdata` command
- Loads initial fixtures
- Creates default products
- Sets up basic data

---

## 🔧 Integration with Existing Commands

The commands work alongside existing management commands:

```bash
# Full setup workflow
python manage.py reset_database --repopulate
python manage.py add_business_owner --email owner@javamellow.com
python manage.py create_default_products
python manage.py create_riverside_herald_user  # If needed
python manage.py create_sample_articles  # If needed
```

---

## ⚠️ Important Notes

### Security
- **Never use `--no-input` in production**
- **Always update placeholder API keys**
- **Use strong passwords for business owners**

### Database Reset
- **Backup database before reset** (if you have important data)
- **Flush method is safer** than drop method
- **Production warning** requires typing "DELETE ALL DATA"

### Riverside Herald Access
- Business owners get `business_owner` role in news Profile
- They can manage content in Riverside Herald
- They have their own company for e-commerce
- They are members of Riverside Herald company

---

## 📊 Example Output

### `add_business_owner` Output:
```
Creating business owner...
✓ Created user: owner@javamellow.com (owner)
✓ Created company: JavaMellow (ID: 550e8400-e29b-41d4-a716-446655440000)
✓ Created integration settings with placeholder API keys
✓ Found Riverside Herald company: Riverside Herald
✓ Added user as member of Riverside Herald company
✓ Created news profile with role: business_owner

✅ Setup complete!

📋 User Details:
  Email: owner@javamellow.com
  Username: owner
  Password: secure_password123
  Full Name: John Doe
  Is Staff: True
  Is Active: True

🏢 Business Company Details:
  Name: JavaMellow
  Slug: javamellow
  ID: 550e8400-e29b-41d4-a716-446655440000
  Status: active
  Plan: premium

🔑 Integration Settings:
  Yoco Public Key: pk_test_placeholder_replace_with_real_key
  Yoco Sandbox Mode: True
  Courier Service: courier_guy
  Courier Sandbox Mode: True
  ⚠️  Remember to replace placeholder API keys with real keys!

📰 Riverside Herald Access:
  Company: Riverside Herald
  Company ID: [riverside-company-id]
  News Profile Role: business_owner
  Can Manage Content: Yes
```

---

## 🎯 Use Cases

### Use Case 1: New Business Owner Setup
```bash
python manage.py add_business_owner \
    --email newbusiness@example.com \
    --name "New Business" \
    --password "secure123" \
    --full-name "Jane Smith"
```

### Use Case 2: Reset Development Database
```bash
# Quick reset (flush only)
python manage.py reset_database --flush-only --repopulate

# Complete reset
python manage.py reset_database --repopulate
```

### Use Case 3: Production Reset (with confirmation)
```bash
# Will prompt for confirmation
python manage.py reset_database --repopulate
# Type "DELETE ALL DATA" when prompted
```

---

## 🔗 Related Commands

- `setupdata` - Initial database setup
- `create_default_products` - Create default products
- `create_riverside_herald_user` - Create Riverside Herald user
- `create_sample_articles` - Create sample articles
- `createsuperuser` - Create Django admin user

---

*Commands created for JavaMellow project*  
*Last Updated: 2024*

