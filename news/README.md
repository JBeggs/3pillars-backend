# News Platform App

This Django app provides a multi-tenant news platform and business directory for The Riverside Herald.

## Features

- **Articles**: News articles with categories, tags, media, and comments
- **Business Directory**: Business listings with reviews and ratings
- **Media Management**: File uploads, galleries, and media organization
- **RSS Feeds**: Automated content aggregation from RSS sources
- **Notifications**: User notifications with company context
- **Team & Testimonials**: Team member profiles and testimonials

## Multi-Tenancy

All models (except `Profile` and `UserSession`) are scoped to `EcommerceCompany`. The company context is determined via:

1. `X-Company-Id` header (primary method)
2. User's owned company (fallback)
3. Query parameter `company_id` (superusers only)

## API Endpoints

All endpoints are under `/api/news/`:

- `/api/news/categories/` - Article categories
- `/api/news/tags/` - Article tags
- `/api/news/media/` - Media files
- `/api/news/galleries/` - Media galleries
- `/api/news/articles/` - News articles
- `/api/news/comments/` - Article comments
- `/api/news/businesses/` - Business directory
- `/api/news/business-reviews/` - Business reviews
- `/api/news/advertisements/` - Advertisements
- `/api/news/rss-sources/` - RSS feed sources
- `/api/news/notifications/` - User notifications
- `/api/news/site-settings/` - Site configuration
- `/api/news/team-members/` - Team members
- `/api/news/testimonials/` - Testimonials

## Authentication

All endpoints require:
- JWT token in `Authorization: Bearer <token>` header
- `X-Company-Id: <company_uuid>` header (for tenant-scoped endpoints)

## Usage Example

```python
import requests

headers = {
    'Authorization': 'Bearer <jwt_token>',
    'X-Company-Id': '<company_uuid>',
    'Content-Type': 'application/json'
}

# Get articles
response = requests.get('http://api.example.com/api/news/articles/', headers=headers)
articles = response.json()

# Create article
data = {
    'title': 'New Article',
    'slug': 'new-article',
    'content': 'Article content...',
    'status': 'draft'
}
response = requests.post('http://api.example.com/api/news/articles/', json=data, headers=headers)
```

## Models

### Tenant-Scoped Models
- `Category` - Article categories
- `Tag` - Article tags
- `Media` - Media files
- `Gallery` - Media galleries
- `Article` - News articles
- `Comment` - Article comments
- `Business` - Business listings
- `BusinessReview` - Business reviews
- `Advertisement` - Advertisements
- `RSSSource` - RSS feed sources
- `Notification` - User notifications (with company context)
- `SiteSetting` - Site settings
- `TeamMember` - Team members
- `Testimonial` - Testimonials
- `AudioRecording` - Audio recordings
- `ContentImport` - Content imports

### Shared Models
- `Profile` - Extended user profiles (NOT tenant-scoped)
- `UserSession` - User session tracking (NOT tenant-scoped)

## Database Tables

All tables are prefixed with `news_`:
- `news_profiles`
- `news_categories`
- `news_tags`
- `news_media`
- `news_galleries`
- `news_articles`
- `news_comments`
- `news_businesses`
- `news_business_reviews`
- `news_advertisements`
- `news_rss_sources`
- `news_notifications`
- `news_site_settings`
- etc.

## Permissions

- `HasCompanyAccess` - Checks user has access to company
- `IsAuthorOrReadOnly` - Only authors can edit their articles
- `IsBusinessOwnerOrReadOnly` - Only owners can edit businesses

## Next Steps

1. Run migrations: `python manage.py makemigrations news`
2. Apply migrations: `python manage.py migrate`
3. Create initial data (categories, settings) if needed
4. Test API endpoints with proper authentication

