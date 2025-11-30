# E-commerce Multi-Tenant API - Quick Start

## Installation

The e-commerce app has been added to Django CRM. To activate it:

### 1. Run Migrations

```bash
cd django-crm
python manage.py makemigrations ecommerce
python manage.py migrate
```

### 2. Create a Company

You can create a company via the Django admin or via API:

**Via Admin:**
1. Go to `/admin/`
2. Navigate to "E-commerce Companies"
3. Click "Add E-commerce Company"
4. Fill in the form and save

**Via API:**
```bash
POST /api/v1/companies/
Authorization: Bearer {your_jwt_token}
Content-Type: application/json

{
  "name": "My Company",
  "slug": "my-company",
  "email": "contact@mycompany.com",
  "currency": "ZAR",
  "timezone": "Africa/Johannesburg"
}
```

### 3. Create a Category

```bash
POST /api/v1/categories/
Authorization: Bearer {your_jwt_token}
Content-Type: application/json

{
  "slug": "classic",
  "name": "Classic",
  "description": "Classic marshmallow flavors"
}
```

### 4. Create a Product

```bash
POST /api/v1/products/
Authorization: Bearer {your_jwt_token}
Content-Type: application/json

{
  "name": "Vanilla Toffee Marshmallow",
  "slug": "vanilla-toffee-marshmallow",
  "description": "Classic vanilla marshmallows with rich toffee undertones",
  "price": 45.00,
  "category": "{category_uuid}",
  "image": "https://cdn.example.com/image.jpg",
  "in_stock": true,
  "status": "active"
}
```

### 5. List Products

```bash
GET /api/v1/products/?category=classic&status=active&page=1&limit=20
Authorization: Bearer {your_jwt_token}
```

## API Endpoints

All endpoints are under `/api/v1/`:

- `GET /api/v1/companies/` - List companies
- `GET /api/v1/companies/me/` - Get current user's company
- `POST /api/v1/companies/` - Create company
- `GET /api/v1/products/` - List products
- `GET /api/v1/products/:id/` - Get product
- `GET /api/v1/products/slug/:slug/` - Get product by slug
- `POST /api/v1/products/` - Create product
- `PUT /api/v1/products/:id/` - Update product
- `DELETE /api/v1/products/:id/` - Delete product
- `POST /api/v1/products/bulk/` - Bulk operations
- `PUT /api/v1/products/:id/stock/` - Update stock
- `GET /api/v1/products/autocomplete/?q=vanilla` - Autocomplete
- `GET /api/v1/categories/` - List categories
- `POST /api/v1/categories/` - Create category
- `POST /api/v1/products/images/upload/` - Upload image
- `POST /api/v1/products/images/upload-multiple/` - Upload multiple images

## Multi-Tenancy

- **Company is automatically determined** from the authenticated user
- Users can only access their own company's data
- Superusers can access all companies (use `?company_id=` param)
- All queries are automatically filtered by company

## Notes

- Products use UUIDs as primary keys
- Slugs are unique within a company (not globally)
- Image uploads currently return placeholder URLs - implement cloud storage for production
- Company is determined from the first company owned by the user

## Next Steps

1. Implement cloud storage for images (S3, Cloudinary)
2. Add JWT company context
3. Implement public endpoints
4. Add image processing (thumbnails, optimization)

