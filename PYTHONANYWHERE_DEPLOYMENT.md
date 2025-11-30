# PythonAnywhere Deployment Guide

This guide will help you deploy Django CRM to PythonAnywhere.

## Prerequisites

1. PythonAnywhere account (free or paid)
2. Git repository with your code
3. MySQL database (included with PythonAnywhere accounts)

## Step 1: Create MySQL Database

1. Log into PythonAnywhere dashboard
2. Go to **Databases** tab
3. Click **Create a new database**
4. Note your database credentials:
   - Database name: `yourusername$crm_db`
   - Username: `yourusername`
   - Password: (set a secure password)
   - Host: `yourusername.mysql.pythonanywhere-services.com`

## Step 2: Clone Your Repository

1. Open a **Bash console** in PythonAnywhere
2. Navigate to your home directory:
   ```bash
   cd ~
   ```
3. Clone your repository:
   ```bash
   git clone git@github.com:JBeggs/3pillars-backend.git
   cd 3pillars-backend
   ```

## Step 3: Set Up Virtual Environment

```bash
# Create virtual environment
python3.10 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

## Step 4: Configure Environment Variables

Create a `.env` file in the `3pillars-backend` directory:

```bash
nano .env
```

Add the following (replace with your actual values):

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourusername.pythonanywhere.com

# Database (PythonAnywhere MySQL)
DB_NAME=yourusername$crm_db
DB_USER=yourusername
DB_PASSWORD=your-database-password
DB_HOST=yourusername.mysql.pythonanywhere-services.com
DB_PORT=3306
PYTHONANYWHERE_USERNAME=yourusername

# Email (optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_PORT=587
EMAIL_USE_TLS=True
```

**Generate a secret key:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## Step 5: Update Settings

The settings file is already configured for PythonAnywhere. Make sure:

1. `ON_PYTHONANYWHERE` is detected automatically
2. Database configuration uses environment variables
3. Static and media files are configured correctly

## Step 6: Run Migrations

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

## Step 7: Collect Static Files

```bash
python manage.py collectstatic --noinput
```

## Step 8: Configure WSGI File

1. Go to **Web** tab in PythonAnywhere dashboard
2. Click **WSGI configuration file** link
3. Replace the content with:

```python
import os
import sys

# Add your project directory to the path
path = '/home/yourusername/3pillars-backend'
if path not in sys.path:
    sys.path.insert(0, path)

# Set environment variables
os.environ['DJANGO_SETTINGS_MODULE'] = 'webcrm.settings'

# Activate virtual environment
activate_this = '/home/yourusername/3pillars-backend/venv/bin/activate_this.py'
with open(activate_this) as f:
    exec(f.read(), {'__file__': activate_this})

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

**Important:** Replace `yourusername` and `your-repo` with your actual values.

## Step 9: Configure Static Files Mapping

In the **Web** tab:

1. **Static files** section:
   - URL: `/static/`
   - Directory: `/home/yourusername/static/static/`

2. **Static files** section (for admin):
   - URL: `/static/admin/`
   - Directory: `/home/yourusername/static/static/admin/`

## Step 10: Configure Media Files Mapping

In the **Web** tab:

1. **Static files** section:
   - URL: `/media/`
   - Directory: `/home/yourusername/media/`

## Step 11: Reload Web App

Click the **Reload** button in the Web tab.

## Step 12: Access Your Application

- Admin: `https://yourusername.pythonanywhere.com/admin/`
- API: `https://yourusername.pythonanywhere.com/api/`
- API Docs: `https://yourusername.pythonanywhere.com/api/docs/`

## Troubleshooting

### Database Connection Issues

1. Check database credentials in `.env`
2. Verify database is running (Databases tab)
3. Test connection:
   ```bash
   python manage.py dbshell
   ```

### Static Files Not Loading

1. Verify static files were collected: `ls ~/static/static/`
2. Check static files mapping in Web tab
3. Ensure `STATIC_ROOT` is correct in settings

### Media Files Not Working

1. Create media directory: `mkdir -p ~/media`
2. Set proper permissions: `chmod 755 ~/media`
3. Check media files mapping in Web tab

### Import Errors

1. Ensure virtual environment is activated in WSGI file
2. Check Python version (use 3.10)
3. Verify all dependencies are installed

### 500 Errors

1. Check error log in **Web** tab → **Error log**
2. Check server log in **Tasks** tab
3. Enable DEBUG temporarily to see detailed errors

## Scheduled Tasks (Optional)

For periodic tasks (like email sending), use PythonAnywhere's **Tasks** tab:

1. Go to **Tasks** tab
2. Create a new scheduled task
3. Example: Run management command daily
   ```bash
   /home/yourusername/3pillars-backend/venv/bin/python /home/yourusername/3pillars-backend/manage.py your_command
   ```

## Security Checklist

- [ ] Set `DEBUG=False` in production
- [ ] Use strong `SECRET_KEY`
- [ ] Set proper `ALLOWED_HOSTS`
- [ ] Use HTTPS (PythonAnywhere provides this)
- [ ] Keep dependencies updated
- [ ] Use environment variables for secrets
- [ ] Set up proper database backups

## Updating Your Application

1. Pull latest changes:
   ```bash
   cd ~/3pillars-backend
   git pull
   ```

2. Activate virtual environment:
   ```bash
   source venv/bin/activate
   ```

3. Install new dependencies (if any):
   ```bash
   pip install -r requirements.txt
   ```

4. Run migrations:
   ```bash
   python manage.py migrate
   ```

5. Collect static files:
   ```bash
   python manage.py collectstatic --noinput
   ```

6. Reload web app in dashboard

## Notes

- Free accounts have limited resources and may sleep after inactivity
- Paid accounts have better performance and no sleep
- Database backups are recommended (use PythonAnywhere's backup feature)
- Static files are served efficiently by PythonAnywhere
- Media files are stored in your home directory

## Support

- PythonAnywhere Help: https://help.pythonanywhere.com/
- Django Documentation: https://docs.djangoproject.com/
- Check error logs in PythonAnywhere dashboard

