# E-commerce Multi-Tenant Product Management

This Django app implements a **multi-tenant e-commerce product management system** based on the JavaMellow Backend API Specification.

## Overview

The e-commerce app provides:
- **Multi-tenant architecture** - Each company has isolated product data
- **Company management** - Create and manage companies/organizations
- **Product management** - Full CRUD operations for products
- **Category management** - Company-scoped product categories
- **Image management** - Upload and manage product images
- **RESTful API** - Complete API following the JavaMellow specification

## Features

### Multi-Tenancy
- **Company isolation** - All data is scoped to companies
- **Automatic filtering** - Products, categories, and images are automatically filtered by company
- **Security** - Users can only access their own company's data (unless superuser)

### Product Management
- Full product CRUD operations
- Advanced filtering (category, status, price range, tags, etc.)
- Slug-based product lookup
- Bulk operations (update, delete, archive)
- Stock management
- SEO fields
- Product images

### API Endpoints

All endpoints are prefixed with `/api/v1/`:

- **Companies**: `/api/v1/companies/`
- **Products**: `/api/v1/products/`
- **Categories**: `/api/v1/categories/`
- **Images**: `/api/v1/products/images/`

## Models

### EcommerceCompany
Multi-tenant company model with:
- Company information (name, email, address, etc.)
- Settings (currency, timezone, language)
- Status and plan management
- Resource limits

### EcommerceProduct
Product model with:
- Company-scoped products
- Pricing (price, compare_at_price, cost_price)
- Inventory management
- Categories and tags
- SEO fields
- Images

### Category
Company-scoped product categories

### ProductImage
Product images organized by company

## API Usage

### Authentication
All endpoints require authentication. Company context is automatically determined from the authenticated user.

### Example Requests

**List Products:**
```
GET /api/v1/products/?category=classic&status=active&page=1&limit=20
```

**Get Product by Slug:**
```
GET /api/v1/products/slug/vanilla-toffee-marshmallow/
```

**Create Product:**
```
POST /api/v1/products/
{
  "name": "Vanilla Toffee Marshmallow",
  "slug": "vanilla-toffee-marshmallow",
  "description": "Classic vanilla marshmallows...",
  "price": 45.00,
  "category": "category-uuid",
  "image": "https://cdn.example.com/image.jpg",
  "in_stock": true,
  "status": "active"
}
```

**Upload Image:**
```
POST /api/v1/products/images/upload/
Content-Type: multipart/form-data
file: [binary]
```

## Setup

1. **Add to INSTALLED_APPS** (already done):
   ```python
   'ecommerce.apps.EcommerceConfig',
   ```

2. **Run migrations:**
   ```bash
   python manage.py makemigrations ecommerce
   python manage.py migrate
   ```

3. **Create superuser** (if needed):
   ```bash
   python manage.py createsuperuser
   ```

## Security

- **Company isolation** - All queries are filtered by company
- **Permission checks** - Users can only access their own company's data
- **Superuser access** - Superusers can access all companies (with `?company_id=` param)

## Future Enhancements

- [ ] Cloud storage integration (S3, Cloudinary) for images
- [ ] Image optimization and thumbnail generation
- [ ] Product import/export functionality
- [ ] Analytics and reporting
- [ ] Multi-company support per user
- [ ] API key authentication
- [ ] Rate limiting per company

## Documentation

See the full API specification in the project documentation:
- JavaMellow Backend API Specification

## Notes

- Products use UUIDs as primary keys
- Slugs are unique within a company (not globally)
- Images currently return placeholder URLs - implement cloud storage for production
- Company is determined from authenticated user (first company owned by user)

