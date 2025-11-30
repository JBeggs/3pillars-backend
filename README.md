# Three Pillars Backend

**Backend API for Three Pillars Business Management System**

A comprehensive Django-based backend system powering the Three Pillars business ecosystem, including customer relationship management, multi-tenant e-commerce, business registration workflows, and real-time notifications.

---

## 🎯 What is This?

This is the **backend API** for the **Three Pillars** business management system, which serves three core business pillars:

1. **Operations & Management** - Project and task management
2. **Sales & Marketing** - Technical sales and customer relations  
3. **Product & Development** - Software development and technical solutions

### System Architecture

```
┌─────────────────┐
│  React Web App  │  (3piller - Customer-facing portal)
│   (3piller)     │
└────────┬────────┘
         │ HTTP/REST API
         ▼
┌─────────────────┐
│  Django Backend │  ← You are here (3pillars-backend)
│   (This Repo)    │
└────────┬────────┘
         │
         ├──► Flutter Mobile App (Staff/Team management)
         ├──► Firebase Cloud Messaging (Push notifications)
         ├──► Yoco Payment Gateway (Multi-tenant payments)
         └──► Courier Guy / Pudo (Shipping integration)
```

---

## 🚀 Key Features

### Core CRM Functionality
- ✅ **Deal Management** - Track sales opportunities and deals
- ✅ **Contact & Company Management** - Comprehensive customer database
- ✅ **Task & Project Management** - Team collaboration and workflow
- ✅ **Chat & Messaging** - Internal communication system
- ✅ **Lead Management** - Convert leads to deals
- ✅ **Analytics & Reporting** - Sales funnel, income summary, lead sources

### Multi-Tenant E-Commerce
- ✅ **Company-Scoped Products** - Each business manages their own catalog
- ✅ **Shopping Cart System** - Server-side cart management
- ✅ **Order Management** - Complete order lifecycle
- ✅ **Payment Integration** - Yoco payment gateway (per company)
- ✅ **Shipping Integration** - Courier Guy / Pudo pickup points (per company)
- ✅ **Sales Analytics** - Revenue tracking, top products, trends

### Business Registration & Onboarding
- ✅ **Business Registration** - Complete registration workflow
- ✅ **Product Assignment** - Automatic product linking (e.g., micro-sites)
- ✅ **Deal Creation** - Automatic deal creation for approval
- ✅ **Staff Notifications** - Chat messages + Firebase push notifications
- ✅ **Company Activation** - Automatic activation when deal is completed

### Real-Time Notifications
- ✅ **Firebase Cloud Messaging** - Push notifications to mobile app
- ✅ **Per-User Settings** - Customizable notification preferences
- ✅ **Company-Scoped** - Notifications filtered by company context
- ✅ **Multiple Notification Types** - Deal updates, task assignments, messages

### REST API
- ✅ **JWT Authentication** - Secure token-based auth
- ✅ **Full CRUD Operations** - Complete API for all entities
- ✅ **Advanced Filtering** - Search and filter capabilities
- ✅ **File Uploads** - Support for images, audio, documents
- ✅ **API Documentation** - Swagger/OpenAPI docs

---

## 📋 Technology Stack

- **Framework**: Django 5.2.8+ (Python 3.11+)
- **API**: Django REST Framework
- **Authentication**: JWT (Simple JWT)
- **Database**: SQLite (dev) / MySQL (PythonAnywhere) / PostgreSQL
- **Real-Time**: Firebase Cloud Messaging
- **Payments**: Yoco Payment Gateway
- **Shipping**: Courier Guy / Pudo
- **Deployment**: PythonAnywhere ready

---

## 🏗️ Project Structure

```
3pillars-backend/
├── api/              # REST API endpoints
├── crm/              # Core CRM models (Deals, Contacts, Companies)
├── common/           # Shared models (Products, Departments, Users)
├── ecommerce/          # Multi-tenant e-commerce
├── fcm/              # Firebase Cloud Messaging
├── tasks/            # Task & project management
├── chat/             # Internal messaging
├── analytics/        # Sales analytics & reports
├── massmail/         # Email marketing
├── webcrm/           # Django settings & configuration
└── docs/             # Documentation
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- pip
- Virtual environment (recommended)

### Installation

1. **Clone the repository:**
   ```bash
   git clone git@github.com:JBeggs/3pillars-backend.git
   cd 3pillars-backend
   ```

2. **Create and activate virtual environment:**
   ```bash
   python3.11 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env  # Create .env file
   # Edit .env with your settings
   ```

5. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser:**
   ```bash
   python manage.py createsuperuser
   ```

7. **Create default products:**
   ```bash
   python manage.py create_default_products
   ```

8. **Run development server:**
   ```bash
   python manage.py runserver
   ```

9. **Access the application:**
   - Admin Panel: http://localhost:8000/admin/
   - API: http://localhost:8000/api/
   - API Docs: http://localhost:8000/api/docs/

---

## 📚 Documentation

### Setup & Configuration
- **[Local Setup Guide](docs/setup/LOCAL_SETUP.md)** - Setting up for local development
- **[PythonAnywhere Deployment](docs/deployment/PYTHONANYWHERE_QUICK_START.md)** - Deploy to PythonAnywhere
- **[Deployment Checklist](docs/deployment/DEPLOYMENT_CHECKLIST.md)** - Pre-deployment checklist

### Integrations
- **[Firebase Setup](docs/integrations/FIREBASE_SETUP.md)** - Configure Firebase Cloud Messaging
- **[FCM Integration](docs/integrations/FCM_INTEGRATION.md)** - Push notification setup
- **[FCM Notification Settings](docs/integrations/FCM_NOTIFICATION_SETTINGS.md)** - User notification preferences
- **[Email Setup](docs/integrations/EMAIL_SETUP.md)** - Configure email sending

### Troubleshooting
- **[Database Connection Issues](docs/troubleshooting/DATABASE_CONNECTION_TROUBLESHOOTING.md)** - Fix database connection problems
- **[Database Timeout Fix](docs/troubleshooting/DATABASE_CONNECTION_TIMEOUT_FIX.md)** - Resolve timeout errors
- **[503 Error Fix](docs/troubleshooting/FIX_503_ERROR.md)** - Fix 503 service unavailable errors
- **[Run Migrations](docs/troubleshooting/RUN_MIGRATIONS_NOW.md)** - Migration troubleshooting
- **[Run Setup Data](docs/troubleshooting/RUN_SETUPDATA_LOCALLY.md)** - Initial data setup

### Architecture & Features
- **[Multi-Tenancy Impact](docs/MULTI_TENANCY_IMPACT.md)** - Understanding multi-tenant architecture
- **[Multi-Tenant Setup Complete](docs/MULTI_TENANT_SETUP_COMPLETE.md)** - Multi-tenant implementation details

### Documentation Index
- **[Complete Documentation Index](docs/README.md)** - Browse all documentation organized by category

---

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/login/` - Login and get JWT tokens
- `POST /api/auth/refresh/` - Refresh access token
- `POST /api/auth/register/` - Business registration
- `GET /api/auth/users/` - List users

### CRM
- `GET/POST /api/companies/` - Companies
- `GET/POST /api/contacts/` - Contacts
- `GET/POST /api/deals/` - Deals/Opportunities
- `GET/POST /api/leads/` - Leads
- `GET/POST /api/requests/` - Commercial requests

### Tasks & Projects
- `GET/POST /api/tasks/` - Tasks
- `GET/POST /api/projects/` - Projects
- `GET/POST /api/memos/` - Office memos

### E-Commerce (Multi-Tenant)
- `GET/POST /api/v1/products/` - Products (company-scoped)
- `GET/POST /api/v1/categories/` - Categories (company-scoped)
- `GET/POST /api/v1/carts/` - Shopping carts
- `GET/POST /api/v1/orders/` - Orders

### Chat & Messaging
- `GET/POST /api/chat/` - Chat messages
- `GET /api/chat/for_object/` - Messages for specific objects

### Firebase (FCM)
- `POST /api/fcm/register/` - Register device token
- `GET /api/fcm/settings/` - Get notification settings
- `PUT /api/fcm/settings/` - Update notification settings

**Full API Documentation**: http://localhost:8000/api/docs/ (when server is running)

---

## 🔐 Environment Variables

Create a `.env` file in the project root:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,192.168.1.100

# Database (SQLite for local dev)
# For MySQL/PostgreSQL, set DATABASE_URL or individual DB_* variables

# Firebase
FIREBASE_CREDENTIALS_PATH=./firebase-service-account.json

# Email (optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_PORT=587
EMAIL_USE_TLS=True
```

---

## 🏢 Multi-Tenancy

This system uses **selective multi-tenancy**:

- **E-Commerce App**: Fully multi-tenant (products, orders, carts are company-scoped)
- **FCM Notifications**: Company-scoped (notifications filtered by company)
- **Payment/Shipping**: Company-scoped (each company has their own credentials)
- **Core CRM**: NOT multi-tenant (tasks, deals, contacts are shared)

Company context is determined via:
1. `X-Company-Id` header (primary method)
2. User's owned company (fallback)
3. Query parameter (for superusers only)

---

## 🔔 Business Registration Workflow

When a business registers via the web app:

1. **User & Company Created** - New user account and `EcommerceCompany` record
2. **Product Assigned** - Default product (e.g., "micro-sites") linked to company
3. **Deal Created** - Registration deal created for approval workflow
4. **Staff Notified** - Chat message + Firebase push notification to all staff
5. **Company Activated** - When deal is marked as "won", company status changes to "active"

---

## 📱 Mobile App Integration

The backend powers a **Flutter mobile app** for staff/team management:

- Real-time deal and task management
- Chat and messaging with file attachments
- Push notifications via Firebase
- Deal approval workflows (e.g., micro-sites approval)
- Task creation from deals with product details

---

## 🌐 Web App Integration

The backend powers a **React web app** (3piller) for customer interactions:

- Business registration
- Service requests
- Product management (for registered businesses)
- Customer dashboard

---

## 🚢 Deployment

### PythonAnywhere

See **[PythonAnywhere Quick Start](docs/deployment/PYTHONANYWHERE_QUICK_START.md)** for detailed deployment instructions.

Quick steps:
1. Clone repository
2. Create virtual environment
3. Install dependencies
4. Configure `.env` file
5. Run migrations
6. Collect static files
7. Configure WSGI file
8. Map static/media files

---

## 🧪 Testing

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test api
python manage.py test ecommerce
```

---

## 📦 Dependencies

Key dependencies:
- Django 5.2.8+
- Django REST Framework 3.15.2
- djangorestframework-simplejwt 5.3.1
- firebase-admin 6.5.0
- django-cors-headers 4.3.1
- pymysql 1.1.0 (for PythonAnywhere MySQL)

See `requirements.txt` for complete list.

---

## 🤝 Contributing

This is a private repository for the Three Pillars business system. For internal development:

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit for review

---

## 📄 License

This project is proprietary software for Three Pillars business operations.

---

## 🔗 Related Repositories

- **3piller** - React web application (customer-facing)
- **flutter_crm** - Flutter mobile application (staff/team)

---

## 📞 Support

For issues or questions:
- Check the [documentation](docs/) first
- Review [troubleshooting guides](docs/troubleshooting/)
- Check error logs in Django admin

---

## 🎯 Project Status

See [DEVELOPMENT_STATUS.md](../DEVELOPMENT_STATUS.md) in the parent directory for current development status and roadmap.

---

**Built with ❤️ for Three Pillars Business**
