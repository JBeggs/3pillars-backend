# PythonAnywhere Quick Start Guide

**Quick deployment checklist for Django CRM on PythonAnywhere**

---

## 🚀 Quick Deployment Steps

### 1. Prerequisites
- [ ] PythonAnywhere account (free or paid)
- [ ] Git repository access
- [ ] Database credentials ready

### 2. Initial Setup (First Time Only)

#### A. Create MySQL Database
1. Log into PythonAnywhere dashboard
2. Go to **Databases** tab
3. Click **Create a new database**
4. Note your credentials:
   - Database name: `yourusername$crm_db`
   - Username: `yourusername`
   - Password: (set secure password)
   - Host: `yourusername.mysql.pythonanywhere-services.com`

#### B. Clone Repository
```bash
cd ~
git clone git@github.com:JBeggs/3pillars-backend.git 3pillars-backend
cd 3pillars-backend
```

#### C. Create Virtual Environment
```bash
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

**Note:** If MySQL installation fails, install MySQL client first:
```bash
# In PythonAnywhere bash console
pip install mysqlclient
# If that fails, try:
pip install pymysql
# Then add to settings.py: import pymysql; pymysql.install_as_MySQLdb()
```

#### D. Create .env File
```bash
nano .env
```

Add these variables (replace `yourusername` with your actual username):
```env
# Django Settings
SECRET_KEY=generate-new-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourusername.pythonanywhere.com
PYTHONANYWHERE_USERNAME=yourusername

# Database
DB_NAME=yourusername$crm_db
DB_USER=yourusername
DB_PASSWORD=your-database-password
DB_HOST=yourusername.mysql.pythonanywhere-services.com
DB_PORT=3306

# Firebase (if using)
FIREBASE_CREDENTIALS_PATH=/home/yourusername/3pillars-backend/firebase-service-account.json

# Email (optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_PORT=587
EMAIL_USE_TLS=True
```

**Generate SECRET_KEY:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 3. Database Setup

```bash
# Activate virtual environment
source venv/bin/activate

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Create default products (if needed)
python manage.py create_default_products
```

### 4. Collect Static Files

```bash
python manage.py collectstatic --noinput
```

This will create static files in `~/static/static/`

### 5. Configure WSGI File

1. Go to **Web** tab in PythonAnywhere dashboard
2. Click **WSGI configuration file** link
3. Replace entire content with:

```python
import os
import sys

# Add your project directory to the path
path = '/home/yourusername/3pillars-backend'
if path not in sys.path:
    sys.path.insert(0, path)

# Set environment variables
os.environ['DJANGO_SETTINGS_MODULE'] = 'webcrm.settings'
os.environ['PYTHONANYWHERE_USERNAME'] = 'yourusername'

# Activate virtual environment
activate_this = '/home/yourusername/3pillars-backend/venv/bin/activate_this.py'
if os.path.exists(activate_this):
    with open(activate_this) as f:
        exec(f.read(), {'__file__': activate_this})

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

**Important:** Replace `yourusername` with your actual PythonAnywhere username.

### 6. Configure Static Files Mapping

In the **Web** tab, under **Static files** section:

1. **Static files:**
   - URL: `/static/`
   - Directory: `/home/yourusername/static/static/`

2. **Admin static files (if needed):**
   - URL: `/static/admin/`
   - Directory: `/home/yourusername/static/static/admin/`

### 7. Configure Media Files Mapping

In the **Web** tab, under **Static files** section:

- URL: `/media/`
- Directory: `/home/yourusername/media/`

**Create media directory:**
```bash
mkdir -p ~/media
chmod 755 ~/media
```

### 8. Reload Web App

Click the **Reload** button (green button) in the **Web** tab.

### 9. Test Your Deployment

- Admin: `https://yourusername.pythonanywhere.com/admin/`
- API: `https://yourusername.pythonanywhere.com/api/`
- Landing: `https://yourusername.pythonanywhere.com/`

---

## 🔄 Updating Your Application

When you need to update:

```bash
cd ~/3pillars-backend
source venv/bin/activate
git pull
pip install -r requirements.txt  # If requirements changed
python manage.py migrate
python manage.py collectstatic --noinput
```

Then **Reload** web app in dashboard.

---

## 🐛 Common Issues & Fixes

### Issue: Database Connection Error
**Fix:**
1. Check `.env` file has correct database credentials
2. Verify database is running (Databases tab)
3. Test connection: `python manage.py dbshell`

### Issue: Static Files Not Loading
**Fix:**
1. Verify static files collected: `ls ~/static/static/`
2. Check static files mapping in Web tab
3. Ensure `STATIC_ROOT` is `~/static/static`

### Issue: 500 Internal Server Error
**Fix:**
1. Check **Error log** in Web tab
2. Check **Server log** in Web tab
3. Temporarily set `DEBUG=True` in `.env` to see detailed errors
4. Check WSGI file path is correct

### Issue: Import Errors
**Fix:**
1. Verify virtual environment path in WSGI file
2. Check Python version (should be 3.11)
3. Ensure all dependencies installed: `pip install -r requirements.txt`

### Issue: MySQL Client Not Found
**Fix:**
```bash
# Try installing mysqlclient
pip install mysqlclient

# If that fails, use pymysql instead
pip install pymysql
```

Then add to `webcrm/settings.py` at the top (after imports):
```python
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass
```

### Issue: Firebase Not Working
**Fix:**
1. Ensure `firebase-service-account.json` is uploaded to project directory
2. Check `FIREBASE_CREDENTIALS_PATH` in `.env` points to correct path
3. Verify file permissions: `chmod 644 firebase-service-account.json`

---

## 📋 Pre-Deployment Checklist

Before deploying, ensure:

- [ ] All migrations are created and tested locally
- [ ] `DEBUG=False` in production `.env`
- [ ] Strong `SECRET_KEY` generated
- [ ] `ALLOWED_HOSTS` includes your PythonAnywhere domain
- [ ] Database credentials are correct
- [ ] Static files collected successfully
- [ ] Media directory created and has proper permissions
- [ ] WSGI file configured correctly
- [ ] Static/media file mappings set up
- [ ] Firebase credentials uploaded (if using FCM)
- [ ] Email settings configured (if using email)

---

## 🔐 Security Checklist

- [ ] `DEBUG=False` in production
- [ ] Strong `SECRET_KEY` (not default)
- [ ] `ALLOWED_HOSTS` set correctly
- [ ] Database password is secure
- [ ] Environment variables not committed to git
- [ ] `.env` file has proper permissions (`chmod 600 .env`)
- [ ] Firebase service account file not publicly accessible

---

## 📝 Environment Variables Reference

Required variables in `.env`:

```env
# Required
SECRET_KEY=...
DEBUG=False
ALLOWED_HOSTS=yourusername.pythonanywhere.com
PYTHONANYWHERE_USERNAME=yourusername
DB_NAME=yourusername$crm_db
DB_USER=yourusername
DB_PASSWORD=...
DB_HOST=yourusername.mysql.pythonanywhere-services.com

# Optional
FIREBASE_CREDENTIALS_PATH=...
EMAIL_HOST=...
EMAIL_HOST_USER=...
EMAIL_HOST_PASSWORD=...
```

---

## 🆘 Getting Help

1. **Check Error Logs:**
   - Web tab → Error log
   - Web tab → Server log

2. **PythonAnywhere Help:**
   - https://help.pythonanywhere.com/

3. **Django Documentation:**
   - https://docs.djangoproject.com/

4. **Check Application Logs:**
   ```bash
   tail -f ~/logs/yourusername.pythonanywhere.com.error.log
   ```

---

## 📦 File Structure on PythonAnywhere

```
/home/yourusername/
├── 3pillars-backend/
│   ├── venv/
│   ├── .env
│   ├── manage.py
│   ├── firebase-service-account.json
│   └── ...
├── static/
│   └── static/          # Collected static files
└── media/               # User uploaded files
```

---

## ✅ Post-Deployment Verification

After deployment, verify:

1. **Admin Panel:**
   - Can log in
   - Static files load correctly
   - Can create/edit records

2. **API Endpoints:**
   - `/api/auth/login/` works
   - `/api/deals/` returns data
   - CORS headers present

3. **Static Files:**
   - Admin CSS/JS loads
   - Images display correctly

4. **Media Files:**
   - Can upload files
   - Files are accessible via URL

5. **Database:**
   - Can query data
   - Migrations applied
   - Superuser created

---

*Last Updated: December 2024*

