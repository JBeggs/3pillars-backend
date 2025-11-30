# Local Development Setup

This guide will help you set up the Django CRM for local development before deploying to PythonAnywhere.

## Prerequisites

- Python 3.10 or higher
- pip
- Virtual environment (recommended)

## Setup Steps

### 1. Create and Activate Virtual Environment

```bash
cd django-crm
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows
```

### 2. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Set Up Environment Variables

Create a `.env` file in the `django-crm` directory:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (SQLite for local dev, or use PostgreSQL/MySQL)
# For SQLite, no database config needed
# For PostgreSQL:
# DB_NAME=your_db_name
# DB_USER=your_db_user
# DB_PASSWORD=your_db_password
# DB_HOST=localhost
# DB_PORT=5432

# For MySQL:
# DB_NAME=your_db_name
# DB_USER=your_db_user
# DB_PASSWORD=your_db_password
# DB_HOST=localhost
# DB_PORT=3306
```

**Generate a secret key:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 4. Run Migrations

```bash
python manage.py migrate
```

### 5. Create Superuser

```bash
python manage.py createsuperuser
```

### 6. Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### 7. Run Development Server

```bash
python manage.py runserver
```

The application will be available at `http://localhost:8000`

## WhiteNoise Configuration

The settings are configured to:
- **Use WhiteNoise locally** - For serving static files during development
- **Skip WhiteNoise on PythonAnywhere** - PythonAnywhere serves static files automatically

If WhiteNoise is not installed, the application will still run (it will just skip the middleware). However, for best local development experience, install it:

```bash
pip install whitenoise==6.6.0
```

## Troubleshooting

### ModuleNotFoundError: No module named 'whitenoise'

**Solution 1:** Install whitenoise (recommended for local dev):
```bash
pip install whitenoise==6.6.0
```

**Solution 2:** The settings are already configured to handle missing whitenoise gracefully. The app should still run, but static files may not be served optimally.

### Database Connection Issues

- **SQLite**: Works out of the box, no configuration needed
- **PostgreSQL**: Install `psycopg2-binary` (already in requirements.txt)
- **MySQL**: Install MySQL client libraries first, then `mysqlclient` (see requirements-mysql.txt)

### Static Files Not Loading

1. Run `python manage.py collectstatic`
2. Ensure `STATIC_ROOT` is set correctly in settings
3. For local dev, WhiteNoise will serve static files automatically

### Port Already in Use

If port 8000 is in use:
```bash
python manage.py runserver 8001
```

## Next Steps

1. Test the API endpoints: `http://localhost:8000/api/`
2. Access admin panel: `http://localhost:8000/admin/`
3. Test e-commerce endpoints: `http://localhost:8000/api/v1/`
4. View API documentation: `http://localhost:8000/api/docs/`

## Preparing for PythonAnywhere Deployment

Before deploying to PythonAnywhere:

1. Set `DEBUG=False` in production
2. Update `ALLOWED_HOSTS` with your PythonAnywhere domain
3. Configure production database credentials
4. Review `PYTHONANYWHERE_DEPLOYMENT.md` for deployment steps

